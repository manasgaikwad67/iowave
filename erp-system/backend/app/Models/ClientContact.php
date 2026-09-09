<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Spatie\Activitylog\Traits\LogsActivity;
use Spatie\Activitylog\LogOptions;

class ClientContact extends Model
{
    use HasFactory, LogsActivity;

    protected $fillable = [
        'client_id',
        'first_name',
        'last_name',
        'email',
        'phone',
        'mobile',
        'job_title',
        'department',
        'is_primary',
        'is_billing_contact',
        'is_technical_contact',
        'notes',
        'is_active',
    ];

    protected $casts = [
        'is_primary' => 'boolean',
        'is_billing_contact' => 'boolean',
        'is_technical_contact' => 'boolean',
        'is_active' => 'boolean',
    ];

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['first_name', 'last_name', 'email', 'is_primary'])
            ->logOnlyDirty();
    }

    public function client(): BelongsTo
    {
        return $this->belongsTo(Client::class);
    }

    public function fullName(): string
    {
        return "{$this->first_name} {$this->last_name}";
    }
}