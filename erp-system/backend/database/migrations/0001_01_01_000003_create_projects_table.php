<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('projects', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('code', 20)->unique();
            $table->text('description')->nullable();
            $table->foreignId('client_id')->nullable()->constrained()->nullOnDelete();
            $table->foreignId('department_id')->nullable()->constrained()->nullOnDelete();
            $table->foreignId('project_manager_id')->nullable()->constrained('users')->nullOnDelete();
            $table->enum('status', ['planning', 'active', 'on_hold', 'completed', 'cancelled'])->default('planning');
            $table->enum('priority', ['low', 'medium', 'high', 'critical'])->default('medium');
            $table->date('start_date')->nullable();
            $table->date('end_date')->nullable();
            $table->decimal('estimated_hours', 10, 2)->default(0);
            $table->decimal('estimated_budget', 15, 2)->default(0);
            $table->decimal('actual_hours', 10, 2)->default(0);
            $table->decimal('actual_cost', 15, 2)->default(0);
            $table->enum('billing_type', ['fixed_price', 'time_material', 'retainer', 'milestone'])->default('time_material');
            $table->decimal('hourly_rate', 10, 2)->nullable();
            $table->decimal('fixed_price', 15, 2)->nullable();
            $table->string('currency', 3)->default('USD');
            $table->boolean('is_billable')->default(true);
            $table->boolean('is_active')->default(true);
            $table->timestamps();
            $table->softDeletes();

            $table->index(['status', 'is_active']);
            $table->index(['client_id', 'is_active']);
            $table->index(['project_manager_id', 'is_active']);
        });

        Schema::create('project_members', function (Blueprint $table) {
            $table->id();
            $table->foreignId('project_id')->constrained()->cascadeOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->enum('role', ['owner', 'manager', 'member', 'viewer'])->default('member');
            $table->decimal('hourly_rate', 10, 2)->nullable();
            $table->decimal('allocated_hours', 10, 2)->nullable();
            $table->date('start_date')->nullable();
            $table->date('end_date')->nullable();
            $table->timestamps();

            $table->unique(['project_id', 'user_id']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('project_members');
        Schema::dropIfExists('projects');
    }
};