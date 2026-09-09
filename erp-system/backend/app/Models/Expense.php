<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\MorphMany;
use Spatie\Activitylog\Traits\LogsActivity;
use Spatie\Activitylog\LogOptions;

class Expense extends Model
{
    use HasFactory, LogsActivity;

    protected $fillable = [
        'project_id',
        'user_id',
        'category',
        'description',
        'amount',
        'currency',
        'exchange_rate',
        'expense_date',
        'receipt_number',
        'vendor',
        'is_billable',
        'billing_rate',
        'status',
        'approved_by',
        'approved_at',
        'rejection_reason',
        'notes',
    ];

    protected $casts = [
        'amount' => 'decimal:2',
        'exchange_rate' => 'decimal:6',
        'expense_date' => 'date',
        'is_billable' => 'boolean',
        'billing_rate' => 'decimal:2',
        'approved_at' => 'datetime',
    ];

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['category', 'amount', 'status', 'is_billable'])
            ->logOnlyDirty();
    }

    public function project(): BelongsTo
    {
        return $this->belongsTo(Project::class);
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function approver(): BelongsTo
    {
        return $this->belongsTo(User::class, 'approved_by');
    }

    public function documents(): MorphMany
    {
        return $this->morphMany(Document::class, 'documentable');
    }

    public function getBillableAmountAttribute(): float
    {
        if (!$this->is_billable || !$this->billing_rate) {
            return 0;
        }
        return round($this->amount * $this->billing_rate, 2);
    }

    public function scopeApproved($query)
    {
        return $query->where('status', 'approved');
    }

    public function scopePending($query)
    {
        return $query->where('status', 'pending');
    }
}