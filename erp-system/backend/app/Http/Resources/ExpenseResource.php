<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class ExpenseResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'project' => $this->whenLoaded('project', fn() => new ProjectResource($this->project)),
            'user' => $this->whenLoaded('user', fn() => new UserResource($this->user)),
            'category' => $this->category,
            'description' => $this->description,
            'amount' => $this->amount,
            'currency' => $this->currency,
            'exchange_rate' => $this->exchange_rate,
            'expense_date' => $this->expense_date?->format('Y-m-d'),
            'receipt_number' => $this->receipt_number,
            'vendor' => $this->vendor,
            'is_billable' => $this->is_billable,
            'billing_rate' => $this->billing_rate,
            'billable_amount' => $this->billable_amount,
            'status' => $this->status,
            'approver' => $this->whenLoaded('approver', fn() => new UserResource($this->approver)),
            'approved_at' => $this->approved_at?->toISOString(),
            'rejection_reason' => $this->rejection_reason,
            'notes' => $this->notes,
            'documents' => $this->whenLoaded('documents', fn() => DocumentResource::collection($this->documents)),
            'created_at' => $this->created_at?->toISOString(),
            'updated_at' => $this->updated_at?->toISOString(),
        ];
    }
}