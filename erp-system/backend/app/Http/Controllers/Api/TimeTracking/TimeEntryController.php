<?php

namespace App\Http\Controllers\Api\TimeTracking;

use App\Http\Controllers\Api\BaseController;
use App\Http\Requests\TimeTracking\StoreTimeEntryRequest;
use App\Http\Requests\TimeTracking\UpdateTimeEntryRequest;
use App\Http\Requests\TimeTracking\BulkTimeEntryRequest;
use App\Http\Resources\TimeEntryResource;
use App\Models\TimeEntry;
use App\Models\Project;
use App\Models\Task;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class TimeEntryController extends BaseController
{
    public function index(Request $request): JsonResponse
    {
        $query = TimeEntry::with(['user', 'project', 'task'])
            ->when($request->user_id, fn($q) => $q->where('user_id', $request->user_id))
            ->when($request->project_id, fn($q) => $q->where('project_id', $request->project_id))
            ->when($request->task_id, fn($q) => $q->where('task_id', $request->task_id))
            ->when($request->status, fn($q) => $q->where('status', $request->status))
            ->when($request->is_billable !== null, fn($q) => $q->where('is_billable', $request->boolean('is_billable')))
            ->when($request->start_date, fn($q) => $q->where('date', '>=', $request->start_date))
            ->when($request->end_date, fn($q) => $q->where('date', '<=', $request->end_date));

        // Scope to user's time entries if not admin/approver
        if (!$request->user()->can('time_entries.view_all')) {
            $query->where('user_id', $request->user()->id);
        }

        $timeEntries = $query->orderBy('date', 'desc')
            ->orderBy('created_at', 'desc')
            ->paginate($request->per_page ?? 15);

        return $this->paginated($timeEntries, TimeEntryResource::class);
    }

    public function store(StoreTimeEntryRequest $request): JsonResponse
    {
        $validated = $request->validated();
        
        // Auto-calculate duration if start/end time provided
        if (isset($validated['start_time']) && isset($validated['end_time'])) {
            $start = \Carbon\Carbon::parse($validated['start_time']);
            $end = \Carbon\Carbon::parse($validated['end_time']);
            $validated['duration_minutes'] = $start->diffInMinutes($end);
        }

        $timeEntry = TimeEntry::create(array_merge($validated, [
            'user_id' => $request->user()->id,
            'status' => 'draft',
        ]));

        return $this->created(new TimeEntryResource($timeEntry->load(['user', 'project', 'task'])));
    }

    public function show(Request $request, TimeEntry $timeEntry): JsonResponse
    {
        $this->authorize('view', $timeEntry);
        return $this->success(new TimeEntryResource($timeEntry->load(['user', 'project', 'task', 'approver'])));
    }

    public function update(UpdateTimeEntryRequest $request, TimeEntry $timeEntry): JsonResponse
    {
        $this->authorize('update', $timeEntry);
        
        $validated = $request->validated();
        
        // Auto-calculate duration if start/end time provided
        if (isset($validated['start_time']) && isset($validated['end_time'])) {
            $start = \Carbon\Carbon::parse($validated['start_time']);
            $end = \Carbon\Carbon::parse($validated['end_time']);
            $validated['duration_minutes'] = $start->diffInMinutes($end);
        }

        $timeEntry->update($validated);

        return $this->success(new TimeEntryResource($timeEntry->load(['user', 'project', 'task'])));
    }

    public function destroy(TimeEntry $timeEntry): JsonResponse
    {
        $this->authorize('delete', $timeEntry);
        $timeEntry->delete();

        return $this->noContent();
    }

    public function bulkStore(BulkTimeEntryRequest $request): JsonResponse
    {
        $entries = [];
        
        foreach ($request->entries as $entryData) {
            $validated = $entryData;
            
            if (isset($validated['start_time']) && isset($validated['end_time'])) {
                $start = \Carbon\Carbon::parse($validated['start_time']);
                $end = \Carbon\Carbon::parse($validated['end_time']);
                $validated['duration_minutes'] = $start->diffInMinutes($end);
            }

            $entries[] = TimeEntry::create(array_merge($validated, [
                'user_id' => $request->user()->id,
                'status' => 'draft',
            ]));
        }

        return $this->created(TimeEntryResource::collection($entries));
    }

    public function submitForApproval(Request $request, TimeEntry $timeEntry): JsonResponse
    {
        $this->authorize('update', $timeEntry);
        
        if ($timeEntry->status !== 'draft') {
            return $this->error('Only draft entries can be submitted for approval', 400);
        }

        $timeEntry->update(['status' => 'pending']);

        return $this->success(new TimeEntryResource($timeEntry->load(['user', 'project', 'task'])));
    }

    public function approve(Request $request, TimeEntry $timeEntry): JsonResponse
    {
        $this->authorize('approve', $timeEntry);
        
        if (!in_array($timeEntry->status, ['pending', 'rejected'])) {
            return $this->error('Only pending or rejected entries can be approved', 400);
        }

        $timeEntry->update([
            'status' => 'approved',
            'approved_by' => $request->user()->id,
            'approved_at' => now(),
            'rejection_reason' => null,
        ]);

        // Update project actual hours
        $timeEntry->project->increment('actual_hours', $timeEntry->duration_minutes / 60);
        $timeEntry->project->increment('actual_cost', $timeEntry->billable_amount);

        if ($timeEntry->task) {
            $timeEntry->task->increment('actual_hours', $timeEntry->duration_minutes / 60);
        }

        return $this->success(new TimeEntryResource($timeEntry->load(['user', 'project', 'task', 'approver'])));
    }

    public function reject(Request $request, TimeEntry $timeEntry): JsonResponse
    {
        $this->authorize('approve', $timeEntry);
        
        $request->validate([
            'rejection_reason' => 'required|string',
        ]);

        if ($timeEntry->status !== 'pending') {
            return $this->error('Only pending entries can be rejected', 400);
        }

        $timeEntry->update([
            'status' => 'rejected',
            'approved_by' => $request->user()->id,
            'approved_at' => now(),
            'rejection_reason' => $request->rejection_reason,
        ]);

        return $this->success(new TimeEntryResource($timeEntry->load(['user', 'project', 'task', 'approver'])));
    }

    public function myEntries(Request $request): JsonResponse
    {
        $query = TimeEntry::with(['project', 'task'])
            ->where('user_id', $request->user()->id)
            ->when($request->status, fn($q) => $q->where('status', $request->status))
            ->when($request->start_date, fn($q) => $q->where('date', '>=', $request->start_date))
            ->when($request->end_date, fn($q) => $q->where('date', '<=', $request->end_date));

        $timeEntries = $query->orderBy('date', 'desc')
            ->orderBy('created_at', 'desc')
            ->paginate($request->per_page ?? 15);

        return $this->paginated($timeEntries, TimeEntryResource::class);
    }

    public function weeklySummary(Request $request): JsonResponse
    {
        $startDate = $request->start_date ? \Carbon\Carbon::parse($request->start_date) : now()->startOfWeek();
        $endDate = $request->end_date ? \Carbon\Carbon::parse($request->end_date) : now()->endOfWeek();

        $entries = TimeEntry::with(['project', 'task'])
            ->where('user_id', $request->user()->id)
            ->whereBetween('date', [$startDate, $endDate])
            ->get();

        $summary = [
            'period' => [
                'start' => $startDate->format('Y-m-d'),
                'end' => $endDate->format('Y-m-d'),
            ],
            'total_hours' => round($entries->sum('duration_minutes') / 60, 2),
            'billable_hours' => round($entries->where('is_billable', true)->sum('duration_minutes') / 60, 2),
            'non_billable_hours' => round($entries->where('is_billable', false)->sum('duration_minutes') / 60, 2),
            'by_project' => $entries->groupBy('project_id')->map(fn($group) => [
                'project' => $group->first()->project,
                'hours' => round($group->sum('duration_minutes') / 60, 2),
                'billable_amount' => round($group->sum('billable_amount'), 2),
            ])->values(),
            'by_day' => $entries->groupBy('date')->map(fn($group) => [
                'date' => $group->first()->date->format('Y-m-d'),
                'hours' => round($group->sum('duration_minutes') / 60, 2),
            ])->values(),
            'entries' => TimeEntryResource::collection($entries),
        ];

        return $this->success($summary);
    }

    public function pendingApprovals(Request $request): JsonResponse
    {
        $this->authorize('approve', TimeEntry::class);

        $query = TimeEntry::with(['user', 'project', 'task'])
            ->where('status', 'pending')
            ->when($request->project_id, fn($q) => $q->where('project_id', $request->project_id))
            ->when($request->user_id, fn($q) => $q->where('user_id', $request->user_id));

        $timeEntries = $query->orderBy('date', 'desc')
            ->orderBy('created_at', 'desc')
            ->paginate($request->per_page ?? 15);

        return $this->paginated($timeEntries, TimeEntryResource::class);
    }
}