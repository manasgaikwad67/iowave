<?php

namespace App\Http\Requests\Projects;

use Illuminate\Foundation\Http\FormRequest;

class StoreProjectRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user()->can('projects.create');
    }

    public function rules(): array
    {
        return [
            'name' => 'required|string|max:255',
            'code' => 'required|string|max:20|unique:projects,code',
            'description' => 'nullable|string',
            'client_id' => 'nullable|exists:clients,id',
            'department_id' => 'nullable|exists:departments,id',
            'project_manager_id' => 'nullable|exists:users,id',
            'project_manager_hourly_rate' => 'nullable|numeric|min:0',
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