<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\MorphMany;
use Spatie\Activitylog\Traits\LogsActivity;
use Spatie\Activitylog\LogOptions;

class Task extends Model
{
    use HasFactory, LogsActivity;

    protected $fillable = [
        'project_id',
        'parent_id',
        'title',
        'description',
        'status',
        'priority',
        'assignee_id',
        'creator_id',
        'reporter_id',
        'estimated_hours',
        'actual_hours',
        'start_date',
        'due_date',
        'completed_at',
        'task_type',
        'story_points',
        'sort_order',
    ];

    protected $casts = [
        'estimated_hours' => 'decimal:2',
        'actual_hours' => 'decimal:2',
        'start_date' => 'date',
        'due_date' => 'date',
        'completed_at' => 'datetime',
        'story_points' => 'integer',
        'sort_order' => 'integer',
    ];

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['title', 'status', 'priority', 'assignee_id'])
            ->logOnlyDirty();
    }

    public function project(): BelongsTo
    {
        return $this->belongsTo(Project::class);
    }

    public function parent(): BelongsTo
    {
        return $this->belongsTo(Task::class, 'parent_id');
    }

    public function subtasks(): HasMany
    {
        return $this->hasMany(Task::class, 'parent_id');
    }

    public function assignee(): BelongsTo
    {
        return $this->belongsTo(User::class, 'assignee_id');
    }

    public function creator(): BelongsTo
    {
        return $this->belongsTo(User::class, 'creator_id');
    }

    public function reporter(): BelongsTo
    {
        return $this->belongsTo(User::class, 'reporter_id');
    }

    public function timeEntries(): HasMany
    {
        return $this->hasMany(TimeEntry::class);
    }

    public function comments(): HasMany
    {
        return $this->hasMany(TaskComment::class);
    }

    public function attachments(): MorphMany
    {
        return $this->morphMany(Document::class, 'documentable');
    }

    public function scopeActive($query)
    {
        return $query->whereNotIn('status', ['completed', 'cancelled']);
    }

    public function scopeOverdue($query)
    {
        return $query->where('due_date', '<', now())
            ->whereNotIn('status', ['completed', 'cancelled']);
    }

    public function getProgressAttribute(): float
    {
        if ($this->estimated_hours <= 0) {
            return $this->status === 'completed' ? 100 : 0;
        }
        return min(100, round(($this->actual_hours / $this->estimated_hours) * 100, 2));
    }

    public function getIsOverdueAttribute(): bool
    {
        return $this->due_date && $this->due_date->isPast() && !in_array($this->status, ['completed', 'cancelled']);
    }

    public function getPriorityColorAttribute(): string
    {
        return match($this->priority) {
            'low' => 'gray',
            'medium' => 'blue',
            'high' => 'orange',
            'critical' => 'red',
            default => 'gray',
        };
    }
}