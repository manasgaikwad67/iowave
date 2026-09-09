<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class UserResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'first_name' => $this->first_name,
            'last_name' => $this->last_name,
            'full_name' => $this->fullName(),
            'email' => $this->email,
            'phone' => $this->phone,
            'avatar' => $this->avatar_url,
            'job_title' => $this->job_title,
            'department' => $this->whenLoaded('department', fn() => new DepartmentResource($this->department)),
            'manager' => $this->whenLoaded('manager', fn() => [
                'id' => $this->manager->id,
                'name' => $this->manager->fullName(),
            ]),
            'hire_date' => $this->hire_date?->format('Y-m-d'),
            'employment_type' => $this->employment_type,
            'hourly_rate' => $this->hourly_rate,
            'is_active' => $this->is_active,
            'last_login_at' => $this->last_login_at?->toISOString(),
            'timezone' => $this->timezone,
            'locale' => $this->locale,
            'roles' => $this->whenLoaded('roles', fn() => $this->roles->pluck('name')),
            'permissions' => $this->whenLoaded('permissions', fn() => $this->permissions->pluck('name')),
            'created_at' => $this->created_at?->toISOString(),
            'updated_at' => $this->updated_at?->toISOString(),
        ];
    }
}