<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\MorphMany;
use Spatie\Activitylog\Traits\LogsActivity;
use Spatie\Activitylog\LogOptions;

class Invoice extends Model
{
    use HasFactory, LogsActivity;

    protected $fillable = [
        'invoice_number',
        'client_id',
        'project_id',
        'created_by',
        'status',
        'issue_date',
        'due_date',
        'paid_date',
        'subtotal',
        'tax_rate',
        'tax_amount',
        'discount_amount',
        'total_amount',
        'amount_paid',
        'balance_due',
        'currency',
        'exchange_rate',
        'notes',
        'terms',
        'footer',
    ];

    protected $casts = [
        'issue_date' => 'date',
        'due_date' => 'date',
        'paid_date' => 'date',
        'subtotal' => 'decimal:2',
        'tax_rate' => 'decimal:4',
        'tax_amount' => 'decimal:2',
        'discount_amount' => 'decimal:2',
        'total_amount' => 'decimal:2',
        'amount_paid' => 'decimal:2',
        'balance_due' => 'decimal:2',
        'exchange_rate' => 'decimal:6',
    ];

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['invoice_number', 'status', 'total_amount', 'balance_due'])
            ->logOnlyDirty();
    }

    public function client(): BelongsTo
    {
        return $this->belongsTo(Client::class);
    }

    public function project(): BelongsTo
    {
        return $this->belongsTo(Project::class);
    }

    public function creator(): BelongsTo
    {
        return $this->belongsTo(User::class, 'created_by');
    }

    public function items(): HasMany
    {
        return $this->hasMany(InvoiceItem::class);
    }

    public function payments(): HasMany
    {
        return $this->hasMany(Payment::class);
    }

    public function documents(): MorphMany
    {
        return $this->morphMany(Document::class, 'documentable');
    }

    public function scopeOverdue($query)
    {
        return $query->where('due_date', '<', now())
            ->whereNotIn('status', ['paid', 'cancelled', 'draft']);
    }

    public function scopePending($query)
    {
        return $query->whereIn('status', ['sent', 'viewed', 'partial']);
    }

    public function getStatusColorAttribute(): string
    {
        return match($this->status) {
            'draft' => 'gray',
            'sent' => 'blue',
            'viewed' => 'indigo',
            'partial' => 'orange',
            'paid' => 'green',
            'overdue' => 'red',
            'cancelled' => 'red',
            default => 'gray',
        };
    }

    public function calculateTotals(): void
    {
        $this->subtotal = $this->items()->sum('total');
        $this->tax_amount = round($this->subtotal * ($this->tax_rate / 100), 2);
        $this->total_amount = $this->subtotal + $this->tax_amount - $this->discount_amount;
        $this->balance_due = $this->total_amount - $this->amount_paid;
        $this->save();
    }
}