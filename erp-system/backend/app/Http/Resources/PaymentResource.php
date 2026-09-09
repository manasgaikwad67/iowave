<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class PaymentResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'amount' => $this->amount,
            'currency' => $this->currency,
            'exchange_rate' => $this->exchange_rate,
            'payment_date' => $this->payment_date?->format('Y-m-d'),
            'payment_method' => $this->payment_method,
            'transaction_id' => $this->transaction_id,
            'reference' => $this->reference,
            'notes' => $this->notes,
            'status' => $this->status,
            'processor' => $this->whenLoaded('processor', fn() => new UserResource($this->processor)),
            'created_at' => $this->created_at?->toISOString(),
            'updated_at' => $this->updated_at?->toISOString(),
        ];
    }
}