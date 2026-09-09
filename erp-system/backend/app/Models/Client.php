<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\MorphMany;
use Spatie\Activitylog\Traits\LogsActivity;
use Spatie\Activitylog\LogOptions;

class Client extends Model
{
    use HasFactory, LogsActivity;

    protected $fillable = [
        'name',
        'code',
        'email',
        'phone',
        'website',
        'billing_address',
        'shipping_address',
        'contact_person',
        'contact_email',
        'contact_phone',
        'tax_number',
        'payment_terms',
        'currency',
        'credit_limit',
        'account_manager_id',
        'status',
        'industry',
        'company_size',
        'notes',
        'is_active',
    ];

    protected $casts = [
        'billing_address' => 'array',
        'shipping_address' => 'array',
        'credit_limit' => 'decimal:2',
        'payment_terms' => 'integer',
        'is_active' => 'boolean',
    ];

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['name', 'code', 'email', 'status', 'is_active'])
            ->logOnlyDirty();
    }

    public function accountManager(): BelongsTo
    {
        return $this->belongsTo(User::class, 'account_manager_id');
    }

    public function projects(): HasMany
    {
        return $this->hasMany(Project::class);
    }

    public function invoices(): HasMany
    {
        return $this->hasMany(Invoice::class);
    }

    public function contacts(): HasMany
    {
        return $this->hasMany(ClientContact::class);
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

    public function getTotalInvoicedAttribute(): float
    {
        return $this->invoices()->sum('total_amount');
    }

    public function getOutstandingBalanceAttribute(): float
    {
        return $this->invoices()->where('status', '!=', 'paid')->sum('balance_due');
    }

    public function getStatusColorAttribute(): string
    {
        return match($this->status) {
            'lead' => 'gray',
            'prospect' => 'blue',
            'active' => 'green',
            'on_hold' => 'yellow',
            'inactive' => 'red',
            default => 'gray',
        };
    }
}