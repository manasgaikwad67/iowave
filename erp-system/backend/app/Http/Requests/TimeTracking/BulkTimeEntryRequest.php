<?php

namespace App\Http\Requests\TimeTracking;

use Illuminate\Foundation\Http\FormRequest;

class BulkTimeEntryRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user()->can('time_entries.create');
    }

    public function rules(): array
    {
        return [
            'entries' => 'required|array|min:1|max:50',
            'entries.*.project_id' => 'required|exists:projects,id',
            'entries.*.task_id' => 'nullable|exists:tasks,id',
            'entries.*.date' => 'required|date|before_or_equal:today',
            'entries.*.start_time' => 'nullable|date_format:H:i',
            'entries.*.end_time' => 'nullable|date_format:H:i|after:entries.*.start_time',
            'entries.*.duration_minutes' => 'required_without_all:entries.*.start_time,entries.*.end_time|nullable|integer|min:1|max:1440',
            'entries.*.description' => 'nullable|string',
            'entries.*.is_billable' => 'sometimes|boolean',
            'entries.*.billing_rate' => 'nullable|numeric|min:0',
        ];
    }
}