<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('time_entries', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->foreignId('project_id')->constrained()->cascadeOnDelete();
            $table->foreignId('task_id')->nullable()->constrained()->nullOnDelete();
            $table->date('date');
            $table->time('start_time')->nullable();
            $table->time('end_time')->nullable();
            $table->integer('duration_minutes')->default(0);
            $table->text('description')->nullable();
            $table->boolean('is_billable')->default(true);
            $table->decimal('billing_rate', 10, 2)->nullable();
            $table->enum('status', ['draft', 'pending', 'approved', 'rejected', 'invoiced'])->default('draft');
            $table->foreignId('approved_by')->nullable()->constrained('users')->nullOnDelete();
            $table->timestamp('approved_at')->nullable();
            $table->text('rejection_reason')->nullable();
            $table->timestamps();
            $table->softDeletes();

            $table->index(['user_id', 'date']);
            $table->index(['project_id', 'date']);
            $table->index(['status', 'date']);
            $table->index(['date', 'is_billable']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('time_entries');
    }
};