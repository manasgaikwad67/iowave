<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\Api\Auth\AuthController;
use App\Http\Controllers\Api\Projects\ProjectController;
use App\Http\Controllers\Api\TimeTracking\TimeEntryController;
use App\Http\Controllers\Api\Clients\ClientController;

Route::prefix('auth')->group(function () {
    Route::post('login', [AuthController::class, 'login']);
    Route::post('register', [AuthController::class, 'register']);
    Route::post('forgot-password', [AuthController::class, 'forgotPassword']);
    Route::post('reset-password', [AuthController::class, 'resetPassword']);

    Route::middleware('auth:sanctum')->group(function () {
        Route::post('logout', [AuthController::class, 'logout']);
        Route::get('me', [AuthController::class, 'me']);
        Route::put('profile', [AuthController::class, 'updateProfile']);
        Route::put('password', [AuthController::class, 'updatePassword']);
    });
});

Route::middleware('auth:sanctum')->group(function () {
    // Projects
    Route::apiResource('projects', ProjectController::class);
    Route::get('projects/{project}/members', [ProjectController::class, 'members']);
    Route::post('projects/{project}/members', [ProjectController::class, 'addMember']);
    Route::delete('projects/{project}/members/{user}', [ProjectController::class, 'removeMember']);
    Route::put('projects/{project}/members/{user}', [ProjectController::class, 'updateMember']);
    Route::get('projects/statistics', [ProjectController::class, 'statistics']);

    // Time Entries
    Route::apiResource('time-entries', TimeEntryController::class);
    Route::post('time-entries/bulk', [TimeEntryController::class, 'bulkStore']);
    Route::post('time-entries/{timeEntry}/submit', [TimeEntryController::class, 'submitForApproval']);
    Route::post('time-entries/{timeEntry}/approve', [TimeEntryController::class, 'approve']);
    Route::post('time-entries/{timeEntry}/reject', [TimeEntryController::class, 'reject']);
    Route::get('time-entries/my/entries', [TimeEntryController::class, 'myEntries']);
    Route::get('time-entries/my/weekly-summary', [TimeEntryController::class, 'weeklySummary']);
    Route::get('time-entries/pending/approvals', [TimeEntryController::class, 'pendingApprovals']);

    // Clients
    Route::apiResource('clients', ClientController::class);
    Route::get('clients/{client}/contacts', [ClientController::class, 'contacts']);

    // Users (for dropdowns, assignments)
    Route::get('users', function (Request $request) {
        $query = \App\Models\User::with('department')
            ->when($request->search, fn($q) => $q->where('first_name', 'like', "%{$request->search}%")
                ->orWhere('last_name', 'like', "%{$request->search}%")
                ->orWhere('email', 'like', "%{$request->search}%"))
            ->when($request->role, fn($q) => $q->whereHas('roles', fn($r) => $r->where('name', $request->role)))
            ->when($request->department_id, fn($q) => $q->where('department_id', $request->department_id))
            ->when($request->is_active !== null, fn($q) => $q->where('is_active', $request->boolean('is_active')))
            ->orderBy('first_name');

        return $query->paginate($request->per_page ?? 50);
    });

    // Departments
    Route::get('departments', function (Request $request) {
        return \App\Models\Department::with(['manager', 'children'])
            ->when($request->is_active !== null, fn($q) => $q->where('is_active', $request->boolean('is_active')))
            ->get();
    });

    // Dashboard stats
    Route::get('dashboard/stats', function (Request $request) {
        $user = $request->user();
        $isAdmin = $user->can('projects.view_all');

        $myProjects = \App\Models\Project::whereHas('members', fn($q) => $q->where('user_id', $user->id));
        $allProjects = \App\Models\Project::query();

        $projectQuery = $isAdmin ? $allProjects : $myProjects;

        return [
            'my_projects' => $myProjects->count(),
            'total_projects' => $isAdmin ? $allProjects->count() : null,
            'active_projects' => $projectQuery->clone()->where('status', 'active')->count(),
            'pending_time_entries' => \App\Models\TimeEntry::where('user_id', $user->id)
                ->where('status', 'pending')->count(),
            'draft_time_entries' => \App\Models\TimeEntry::where('user_id', $user->id)
                ->where('status', 'draft')->count(),
            'this_week_hours' => \App\Models\TimeEntry::where('user_id', $user->id)
                ->whereBetween('date', [now()->startOfWeek(), now()->endOfWeek()])
                ->sum('duration_minutes') / 60,
            'pending_approvals' => $user->can('time_entries.approve') 
                ? \App\Models\TimeEntry::where('status', 'pending')->count() 
                : 0,
            'overdue_invoices' => \App\Models\Invoice::where('status', 'overdue')
                ->orWhere(function ($q) {
                    $q->where('due_date', '<', now())
                      ->whereNotIn('status', ['paid', 'cancelled', 'draft']);
                })->count(),
            'outstanding_amount' => \App\Models\Invoice::whereIn('status', ['sent', 'viewed', 'partial', 'overdue'])
                ->sum('balance_due'),
        ];
    });
});