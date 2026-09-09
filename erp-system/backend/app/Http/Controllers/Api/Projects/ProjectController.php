<?php

namespace App\Http\Controllers\Api\Projects;

use App\Http\Controllers\Api\BaseController;
use App\Http\Requests\Projects\StoreProjectRequest;
use App\Http\Requests\Projects\UpdateProjectRequest;
use App\Http\Resources\ProjectResource;
use App\Models\Project;
use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class ProjectController extends BaseController
{
    public function index(Request $request): JsonResponse
    {
        $query = Project::with(['client', 'department', 'projectManager', 'members.user'])
            ->when($request->search, fn($q) => $q->where('name', 'like', "%{$request->search}%")
                ->orWhere('code', 'like', "%{$request->search}%"))
            ->when($request->status, fn($q) => $q->where('status', $request->status))
            ->when($request->client_id, fn($q) => $q->where('client_id', $request->client_id))
            ->when($request->department_id, fn($q) => $q->where('department_id', $request->department_id))
            ->when($request->project_manager_id, fn($q) => $q->where('project_manager_id', $request->project_manager_id))
            ->when($request->is_active !== null, fn($q) => $q->where('is_active', $request->boolean('is_active')));

        // Scope to user's projects if not admin
        if (!$request->user()->can('projects.view_all')) {
            $query->whereHas('members', fn($q) => $q->where('user_id', $request->user()->id));
        }

        $projects = $query->orderBy($request->sort ?? 'created_at', $request->direction ?? 'desc')
            ->paginate($request->per_page ?? 15);

        return $this->paginated($projects, ProjectResource::class);
    }

    public function store(StoreProjectRequest $request): JsonResponse
    {
        $project = Project::create($request->validated());

        // Add project manager as member
        if ($project->project_manager_id) {
            $project->members()->attach($project->project_manager_id, [
                'role' => 'manager',
                'hourly_rate' => $request->project_manager_hourly_rate,
                'allocated_hours' => 40,
                'start_date' => $project->start_date,
            ]);
        }

        return $this->created(new ProjectResource($project->load(['client', 'department', 'projectManager', 'members.user'])));
    }

    public function show(Request $request, Project $project): JsonResponse
    {
        $this->authorize('view', $project);

        return $this->success(
            new ProjectResource($project->load(['client', 'department', 'projectManager', 'members.user', 'tasks']))
        );
    }

    public function update(UpdateProjectRequest $request, Project $project): JsonResponse
    {
        $this->authorize('update', $project);
        $project->update($request->validated());

        return $this->success(new ProjectResource($project->load(['client', 'department', 'projectManager', 'members.user'])));
    }

    public function destroy(Project $project): JsonResponse
    {
        $this->authorize('delete', $project);
        $project->delete();

        return $this->noContent();
    }

    public function members(Request $request, Project $project): JsonResponse
    {
        $this->authorize('view', $project);

        $members = $project->members()->with('user')->get();

        return $this->success(ProjectMemberResource::collection($members));
    }

    public function addMember(Request $request, Project $project): JsonResponse
    {
        $this->authorize('manage_members', $project);

        $validated = $request->validate([
            'user_id' => 'required|exists:users,id',
            'role' => 'required|in:owner,manager,member,viewer',
            'hourly_rate' => 'nullable|numeric|min:0',
            'allocated_hours' => 'nullable|numeric|min:0|max:168',
            'start_date' => 'nullable|date',
            'end_date' => 'nullable|date|after_or_equal:start_date',
        ]);

        $project->members()->syncWithoutDetaching([
            $validated['user_id'] => $validated,
        ]);

        return $this->created(new ProjectMemberResource(
            $project->members()->with('user')->where('user_id', $validated['user_id'])->first()
        ));
    }

    public function removeMember(Request $request, Project $project, User $user): JsonResponse
    {
        $this->authorize('manage_members', $project);
        $project->members()->detach($user->id);

        return $this->noContent();
    }

    public function updateMember(Request $request, Project $project, User $user): JsonResponse
    {
        $this->authorize('manage_members', $project);

        $validated = $request->validate([
            'role' => 'sometimes|in:owner,manager,member,viewer',
            'hourly_rate' => 'sometimes|nullable|numeric|min:0',
            'allocated_hours' => 'sometimes|nullable|numeric|min:0|max:168',
            'start_date' => 'sometimes|nullable|date',
            'end_date' => 'sometimes|nullable|date|after_or_equal:start_date',
        ]);

        $project->members()->updateExistingPivot($user->id, $validated);

        return $this->success(new ProjectMemberResource(
            $project->members()->with('user')->where('user_id', $user->id)->first()
        ));
    }

    public function statistics(Request $request): JsonResponse
    {
        $query = Project::query();

        if (!$request->user()->can('projects.view_all')) {
            $query->whereHas('members', fn($q) => $q->where('user_id', $request->user()->id));
        }

        $stats = [
            'total' => $query->count(),
            'active' => $query->clone()->where('status', 'active')->count(),
            'planning' => $query->clone()->where('status', 'planning')->count(),
            'on_hold' => $query->clone()->where('status', 'on_hold')->count(),
            'completed' => $query->clone()->where('status', 'completed')->count(),
            'cancelled' => $query->clone()->where('status', 'cancelled')->count(),
            'total_budget' => $query->clone()->sum('estimated_budget'),
            'total_actual_cost' => $query->clone()->sum('actual_cost'),
        ];

        return $this->success($stats);
    }
}