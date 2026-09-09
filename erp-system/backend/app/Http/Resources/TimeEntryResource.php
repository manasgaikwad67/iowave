<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class TimeEntryResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'user' => $this->whenLoaded('user', fn() => new UserResource($this->user)),
            'project' => $this->whenLoaded('project', fn() => new ProjectResource($this->project)),
            'task' => $this->whenLoaded('task', fn() => new TaskResource($this->task)),
            'date' => $this->date?->format('Y-m-d'),
            'start_time' => $this->start_time?->format('H:i'),
            'end_time' => $this->end_time?->format('H:i'),
            'duration_minutes' => $this->duration_minutes,
            'duration_hours' => $this->duration_hours,
            'formatted_duration' => $this->formatted_duration,
            'description' => $this->description,
            'is_billable' => $this->is_billable,
            'billing_rate' => $this->billing_rate,
            'billable_amount' => $this->billable_amount,
            'status' => $this->status,
            'approver' => $this->whenLoaded('approver', fn() => new UserResource($this->approver)),
            'approved_at' => $this->approved_at?->toISOString(),
            'rejection_reason' => $this->rejection_reason,
            'created_at' => $this->created_at?->toISOString(),
            'updated_at' => $this->updated_at?->toISOString(),
        ];
    }
}