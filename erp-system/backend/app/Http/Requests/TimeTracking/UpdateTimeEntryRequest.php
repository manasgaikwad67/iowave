<?php

namespace App\Http\Requests\TimeTracking;

use Illuminate\Foundation\Http\FormRequest;

class UpdateTimeEntryRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user()->can('time_entries.edit');
    }

    public function rules(): array
    {
        return [
            'project_id' => 'sometimes|exists:projects,id',
            'task_id' => 'nullable|exists:tasks,id',
            'date' => 'sometimes|date|before_or_equal:today',
            'start_time' => 'nullable|date_format:H:i',
            'end_time' => 'nullable|date_format:H:i|after:start_time',
            'duration_minutes' => 'nullable|integer|min:1|max:1440',
            'description' => 'nullable|string',
            'is_billable' => 'sometimes|boolean',
            'billing_rate' => 'nullable|numeric|min:0',
        ];
    }
}