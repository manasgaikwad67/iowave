<?php

namespace App\Http\Requests\Projects;

use Illuminate\Foundation\Http\FormRequest;

class UpdateProjectRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user()->can('projects.edit');
    }

    public function rules(): array
    {
        $projectId = $this->route('project')?->id;

        return [
            'name' => 'sometimes|string|max:255',
            'code' => 'sometimes|string|max:20|unique:projects,code,' . $projectId,
            'description' => 'nullable|string',
            'client_id' => 'nullable|exists:clients,id',
            'department_id' => 'nullable|exists:departments,id',
            'project_manager_id' => 'nullable|exists:users,id',
            'status' => 'sometimes|in:planning,active,on_hold,completed,cancelled',
            'priority' => 'sometimes|in:low,medium,high,critical',
            'start_date' => 'nullable|date',
            'end_date' => 'nullable|date|after_or_equal:start_date',
            'estimated_hours' => 'nullable|numeric|min:0',
            'estimated_budget' => 'nullable|numeric|min:0',
            'billing_type' => 'sometimes|in:fixed_price,time_material,retainer,milestone',
            'hourly_rate' => 'nullable|numeric|min:0',
            'fixed_price' => 'nullable|numeric|min:0',
            'currency' => 'sometimes|string|size:3',
            'is_billable' => 'sometimes|boolean',
            'is_active' => 'sometimes|boolean',
        ];
    }
}