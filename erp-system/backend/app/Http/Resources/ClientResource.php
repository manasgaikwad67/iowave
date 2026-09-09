<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class ClientResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'name' => $this->name,
            'code' => $this->code,
            'email' => $this->email,
            'phone' => $this->phone,
            'website' => $this->website,
            'billing_address' => $this->billing_address,
            'shipping_address' => $this->shipping_address,
            'contact_person' => $this->contact_person,
            'contact_email' => $this->contact_email,
            'contact_phone' => $this->contact_phone,
            'tax_number' => $this->tax_number,
            'payment_terms' => $this->payment_terms,
            'currency' => $this->currency,
            'credit_limit' => $this->credit_limit,
            'account_manager' => $this->whenLoaded('accountManager', fn() => new UserResource($this->accountManager)),
            'status' => $this->status,
            'status_color' => $this->status_color,
            'industry' => $this->industry,
            'company_size' => $this->company_size,
            'notes' => $this->notes,
            'is_active' => $this->is_active,
            'contacts' => $this->whenLoaded('contacts', fn() => ClientContactResource::collection($this->contacts)),
            'projects_count' => $this->whenCounted('projects'),
            'invoices_count' => $this->whenCounted('invoices'),
            'total_invoiced' => $this->when(isset($this->total_invoiced), $this->total_invoiced),
            'outstanding_balance' => $this->when(isset($this->outstanding_balance), $this->outstanding_balance),
            'created_at' => $this->created_at?->toISOString(),
            'updated_at' => $this->updated_at?->toISOString(),
        ];
    }
}