<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Spatie\Activitylog\Traits\LogsActivity;
use Spatie\Activitylog\LogOptions;

class TimeEntry extends Model
{
    use HasFactory, LogsActivity;

    protected $fillable = [
        'user_id',
        'project_id',
        'task_id',
        'date',
        'start_time',
        'end_time',
        'duration_minutes',
        'description',
        'is_billable',
        'billing_rate',
        'status',
        'approved_by',
        'approved_at',
        'rejection_reason',
    ];

    protected $casts = [
        'date' => 'date',
        'start_time' => 'datetime:H:i',
        'end_time' => 'datetime:H:i',
        'duration_minutes' => 'integer',
        'is_billable' => 'boolean',
        'billing_rate' => 'decimal:2',
        'approved_at' => 'datetime',
    ];

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['date', 'duration_minutes', 'is_billable', 'status'])
            ->logOnlyDirty();
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function project(): BelongsTo
    {
        return $this->belongsTo(Project::class);
    }

    public function task(): BelongsTo
    {
        return $this->belongsTo(Task::class);
    }

    public function approver(): BelongsTo
    {
        return $this->belongsTo(User::class, 'approved_by');
    }

    public function invoiceItem(): \Illuminate\Database\Eloquent\Relations\HasOne
    {
        return $this->hasOne(InvoiceItem::class);
    }

    public function getDurationHoursAttribute(): float
    {
        return round($this->duration_minutes / 60, 2);
    }

    public function getFormattedDurationAttribute(): string
    {
        $hours = floor($this->duration_minutes / 60);
        $minutes = $this->duration_minutes % 60;
        return sprintf('%dh %02dm', $hours, $minutes);
    }

    public function getBillableAmountAttribute(): float
    {
        if (!$this->is_billable || !$this->billing_rate) {
            return 0;
        }
        return round(($this->duration_minutes / 60) * $this->billing_rate, 2);
    }

    public function scopeBillable($query)
    {
        return $query->where('is_billable', true);
    }

    public function scopeApproved($query)
    {
        return $query->where('status', 'approved');
    }

    public function scopePending($query)
    {
        return $query->where('status', 'pending');
    }

    public function scopeDateRange($query, $startDate, $endDate)
    {
        return $query->whereBetween('date', [$startDate, $endDate]);
    }
}