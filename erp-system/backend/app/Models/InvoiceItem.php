<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Spatie\Activitylog\Traits\LogsActivity;
use Spatie\Activitylog\LogOptions;

class InvoiceItem extends Model
{
    use HasFactory, LogsActivity;

    protected $fillable = [
        'invoice_id',
        'time_entry_id',
        'description',
        'quantity',
        'unit_price',
        'tax_rate',
        'discount_percent',
        'total',
        'sort_order',
    ];

    protected $casts = [
        'quantity' => 'decimal:2',
        'unit_price' => 'decimal:2',
        'tax_rate' => 'decimal:4',
        'discount_percent' => 'decimal:2',
        'total' => 'decimal:2',
        'sort_order' => 'integer',
    ];

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['description', 'quantity', 'unit_price', 'total'])
            ->logOnlyDirty();
    }

    public function invoice(): BelongsTo
    {
        return $this->belongsTo(Invoice::class);
    }

    public function timeEntry(): BelongsTo
    {
        return $this->belongsTo(TimeEntry::class);
    }

    public function calculateTotal(): float
    {
        $subtotal = $this->quantity * $this->unit_price;
        $discount = $subtotal * ($this->discount_percent / 100);
        $taxable = $subtotal - $discount;
        $tax = $taxable * ($this->tax_rate / 100);
        return round($taxable + $tax, 2);
    }
}