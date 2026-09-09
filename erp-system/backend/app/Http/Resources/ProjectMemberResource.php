<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class ProjectMemberResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'user' => new UserResource($this->whenLoaded('user')),
            'role' => $this->pivot->role,
            'hourly_rate' => $this->pivot->hourly_rate,
            'allocated_hours' => $this->pivot->allocated_hours,
            'start_date' => $this->pivot->start_date?->format('Y-m-d'),
            'end_date' => $this->pivot->end_date?->format('Y-m-d'),
        ];
    }
}