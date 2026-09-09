<?php

namespace App\Http\Requests\TimeTracking;

use Illuminate\Foundation\Http\FormRequest;

class StoreTimeEntryRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user()->can('time_entries.create');
    }

    public function rules(): array
    {
        return [
            'project_id' => 'required|exists:projects,id',
            'task_id' => 'nullable|exists:tasks,id',
            'date' => 'required|date|before_or_equal:today',
            'start_time' => 'nullable|date_format:H:i',
            'end_time' => 'nullable|date_format:H:i|after:start_time',
            'duration_minutes' => 'required_without_all:start_time,end_time|nullable|integer|min:1|max:1440',
            'description' => 'nullable|string',
            'is_billable' => 'sometimes|boolean',
            'billing_rate' => 'nullable|numeric|min:0',
        ];
    }

    public function withValidator($validator): void
    {
        $validator->after(function ($validator) {
            if (!$this->has('duration_minutes') && (!$this->has('start_time') || !$this->has('end_time'))) {
                $validator->errors()->add('duration', 'Either duration_minutes or both start_time and end_time are required');
            }
        });
    }
}