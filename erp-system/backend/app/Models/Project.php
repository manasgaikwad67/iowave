<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\MorphMany;
use Spatie\Activitylog\Traits\LogsActivity;
use Spatie\Activitylog\LogOptions;

class Project extends Model
{
    use HasFactory, LogsActivity;

    protected $fillable = [
        'name',
        'code',
        'description',
        'client_id',
        'department_id',
        'project_manager_id',
        'status',
        'priority',
        'start_date',
        'end_date',
        'estimated_hours',
        'estimated_budget',
        'actual_hours',
        'actual_cost',
        'billing_type',
        'hourly_rate',
        'fixed_price',
        'currency',
        'is_billable',
        'is_active',
    ];

    protected $casts = [
        'start_date' => 'date',
        'end_date' => 'date',
        'estimated_hours' => 'decimal:2',
        'estimated_budget' => 'decimal:2',
        'actual_hours' => 'decimal:2',
        'actual_cost' => 'decimal:2',
        'hourly_rate' => 'decimal:2',
        'fixed_price' => 'decimal:2',
        'is_billable' => 'boolean',
        'is_active' => 'boolean',
    ];

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['name', 'code', 'status', 'priority', 'is_active'])
            ->logOnlyDirty();
    }

    public function client(): BelongsTo
    {
        return $this->belongsTo(Client::class);
    }

    public function department(): BelongsTo
    {
        return $this->belongsTo(Department::class);
    }

    public function projectManager(): BelongsTo
    {
        return $this->belongsTo(User::class, 'project_manager_id');
    }

    public function members(): BelongsToMany
    {
        return $this->belongsToMany(User::class, 'project_members')
            ->withPivot(['role', 'hourly_rate', 'allocated_hours', 'start_date', 'end_date'])
            ->withTimestamps();
    }

    public function tasks(): HasMany
    {
        return $this->hasMany(Task::class);
    }

    public function timeEntries(): HasMany
    {
        return $this->hasMany(TimeEntry::class);
    }

    public function invoices(): HasMany
    {
        return $this->hasMany(Invoice::class);
    }

    public function expenses(): HasMany
    {
        return $this->hasMany(Expense::class);
    }

    public function documents(): MorphMany
    {
        return $this->morphMany(Document::class, 'documentable');
    }

    public function notes(): MorphMany
    {
        return $this->morphMany(Note::class, 'notable');
    }

    public function scopeActive($query)
    {
        return $query->where('is_active', true);
    }

    public function scopeBillable($query)
    {
        return $query->where('is_billable', true);
    }

    public function getProgressAttribute(): float
    {
        if ($this->estimated_hours <= 0) {
            return 0;
        }
        return min(100, round(($this->actual_hours / $this->estimated_hours) * 100, 2));
    }

    public function getBudgetUtilizationAttribute(): float
    {
        if ($this->estimated_budget <= 0) {
            return 0;
        }
        return min(100, round(($this->actual_cost / $this->estimated_budget) * 100, 2));
    }

    public function getStatusColorAttribute(): string
    {
        return match($this->status) {
            'planning' => 'gray',
            'active' => 'blue',
            'on_hold' => 'yellow',
            'completed' => 'green',
            'cancelled' => 'red',
            default => 'gray',
        };
    }
}