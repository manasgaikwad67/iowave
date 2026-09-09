<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class TaskResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'project_id' => $this->project_id,
            'project' => $this->whenLoaded('project', fn() => [
                'id' => $this->project->id,
                'name' => $this->project->name,
                'code' => $this->project->code,
            ]),
            'parent_id' => $this->parent_id,
            'title' => $this->title,
            'description' => $this->description,
            'status' => $this->status,
            'priority' => $this->priority,
            'priority_color' => $this->priority_color,
            'assignee' => $this->whenLoaded('assignee', fn() => new UserResource($this->assignee)),
            'creator' => $this->whenLoaded('creator', fn() => new UserResource($this->creator)),
            'reporter' => $this->whenLoaded('reporter', fn() => new UserResource($this->reporter)),
            'estimated_hours' => $this->estimated_hours,
            'actual_hours' => $this->actual_hours,
            'progress' => $this->progress,
            'start_date' => $this->start_date?->format('Y-m-d'),
            'due_date' => $this->due_date?->format('Y-m-d'),
            'completed_at' => $this->completed_at?->toISOString(),
            'is_overdue' => $this->is_overdue,
            'task_type' => $this->task_type,
            'story_points' => $this->story_points,
            'subtasks' => TaskResource::collection($this->whenLoaded('subtasks')),
            'subtasks_count' => $this->whenCounted('subtasks'),
            'time_entries_count' => $this->whenCounted('timeEntries'),
            'comments_count' => $this->whenCounted('comments'),
            'created_at' => $this->created_at?->toISOString(),
            'updated_at' => $this->updated_at?->toISOString(),
        ];
    }
}