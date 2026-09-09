<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('expenses', function (Blueprint $table) {
            $table->id();
            $table->foreignId('project_id')->nullable()->constrained()->nullOnDelete();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('category');
            $table->text('description')->nullable();
            $table->decimal('amount', 15, 2);
            $table->string('currency', 3)->default('USD');
            $table->decimal('exchange_rate', 10, 6)->default(1);
            $table->date('expense_date');
            $table->string('receipt_number')->nullable();
            $table->string('vendor')->nullable();
            $table->boolean('is_billable')->default(false);
            $table->decimal('billing_rate', 10, 2)->nullable();
            $table->enum('status', ['draft', 'pending', 'approved', 'rejected', 'reimbursed'])->default('draft');
            $table->foreignId('approved_by')->nullable()->constrained('users')->nullOnDelete();
            $table->timestamp('approved_at')->nullable();
            $table->text('rejection_reason')->nullable();
            $table->text('notes')->nullable();
            $table->timestamps();
            $table->softDeletes();

            $table->index(['project_id', 'status']);
            $table->index(['user_id', 'status']);
            $table->index(['expense_date']);
            $table->index(['category']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('expenses');
    }
};