<?php

namespace App\Http\Requests\Clients;

use Illuminate\Foundation\Http\FormRequest;

class StoreClientRequest extends FormRequest
{
    public function authorize(): bool
    {
        return $this->user()->can('clients.create');
    }

    public function rules(): array
    {
        return [
            'name' => 'required|string|max:255',
            'code' => 'required|string|max:20|unique:clients,code',
            'email' => 'nullable|email|max:255',
            'phone' => 'nullable|string|max:50',
            'website' => 'nullable|url|max:255',
            'billing_address' => 'nullable|array',
            'shipping_address' => 'nullable|array',
            'contact_person' => 'nullable|string|max:255',
            'contact_email' => 'nullable|email|max:255',
            'contact_phone' => 'nullable|string|max:50',
            'tax_number' => 'nullable|string|max:100',
            'payment_terms' => 'sometimes|integer|min:0|max:365',
            'currency' => 'sometimes|string|size:3',
            'credit_limit' => 'nullable|numeric|min:0',
            'account_manager_id' => 'nullable|exists:users,id',
            'status' => 'sometimes|in:lead,prospect,active,on_hold,inactive',
            'industry' => 'nullable|string|max:100',
            'company_size' => 'nullable|in:1-10,11-50,51-200,201-500,501-1000,1000+',
            'notes' => 'nullable|string',
            'is_active' => 'sometimes|boolean',
        ];
    }
}