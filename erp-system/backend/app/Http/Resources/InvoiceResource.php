<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class InvoiceResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'invoice_number' => $this->invoice_number,
            'client' => $this->whenLoaded('client', fn() => new ClientResource($this->client)),
            'project' => $this->whenLoaded('project', fn() => new ProjectResource($this->project)),
            'creator' => $this->whenLoaded('creator', fn() => new UserResource($this->creator)),
            'status' => $this->status,
            'status_color' => $this->status_color,
            'issue_date' => $this->issue_date?->format('Y-m-d'),
            'due_date' => $this->due_date?->format('Y-m-d'),
            'paid_date' => $this->paid_date?->format('Y-m-d'),
            'subtotal' => $this->subtotal,
            'tax_rate' => $this->tax_rate,
            'tax_amount' => $this->tax_amount,
            'discount_amount' => $this->discount_amount,
            'total_amount' => $this->total_amount,
            'amount_paid' => $this->amount_paid,
            'balance_due' => $this->balance_due,
            'currency' => $this->currency,
            'exchange_rate' => $this->exchange_rate,
            'notes' => $this->notes,
            'terms' => $this->terms,
            'footer' => $this->footer,
            'items' => $this->whenLoaded('items', fn() => InvoiceItemResource::collection($this->items)),
            'payments' => $this->whenLoaded('payments', fn() => PaymentResource::collection($this->payments)),
            'is_overdue' => $this->status === 'overdue' || ($this->due_date && $this->due_date->isPast() && !in_array($this->status, ['paid', 'cancelled'])),
            'created_at' => $this->created_at?->toISOString(),
            'updated_at' => $this->updated_at?->toISOString(),
        ];
    }
}