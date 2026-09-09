<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class ProjectResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'name' => $this->name,
            'code' => $this->code,
            'description' => $this->description,
            'client' => $this->whenLoaded('client', fn() => new ClientResource($this->client)),
            'department' => $this->whenLoaded('department', fn() => new DepartmentResource($this->department)),
            'project_manager' => $this->whenLoaded('projectManager', fn() => [
                'id' => $this->projectManager->id,
                'name' => $this->projectManager->fullName(),
            ]),
            'status' => $this->status,
            'status_color' => $this->status_color,
            'priority' => $this->priority,
            'start_date' => $this->start_date?->format('Y-m-d'),
            'end_date' => $this->end_date?->format('Y-m-d'),
            'estimated_hours' => $this->estimated_hours,
            'estimated_budget' => $this->estimated_budget,
            'actual_hours' => $this->actual_hours,
            'actual_cost' => $this->actual_cost,
            'progress' => $this->progress,
            'budget_utilization' => $this->budget_utilization,
            'billing_type' => $this->billing_type,
            'hourly_rate' => $this->hourly_rate,
            'fixed_price' => $this->fixed_price,
            'currency' => $this->currency,
            'is_billable' => $this->is_billable,
            'is_active' => $this->is_active,
            'members' => $this->whenLoaded('members', fn() => ProjectMemberResource::collection($this->members)),
            'tasks_count' => $this->whenCounted('tasks'),
            'time_entries_count' => $this->whenCounted('timeEntries'),
            'created_at' => $this->created_at?->toISOString(),
            'updated_at' => $this->updated_at?->toISOString(),
        ];
    }
}