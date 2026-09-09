<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('clients', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('code', 20)->unique();
            $table->string('email')->nullable();
            $table->string('phone')->nullable();
            $table->string('website')->nullable();
            $table->json('billing_address')->nullable();
            $table->json('shipping_address')->nullable();
            $table->string('contact_person')->nullable();
            $table->string('contact_email')->nullable();
            $table->string('contact_phone')->nullable();
            $table->string('tax_number')->nullable();
            $table->integer('payment_terms')->default(30);
            $table->string('currency', 3)->default('USD');
            $table->decimal('credit_limit', 15, 2)->nullable();
            $table->foreignId('account_manager_id')->nullable()->constrained('users')->nullOnDelete();
            $table->enum('status', ['lead', 'prospect', 'active', 'on_hold', 'inactive'])->default('lead');
            $table->string('industry')->nullable();
            $table->enum('company_size', ['1-10', '11-50', '51-200', '201-500', '501-1000', '1000+'])->nullable();
            $table->text('notes')->nullable();
            $table->boolean('is_active')->default(true);
            $table->timestamps();
            $table->softDeletes();
        });

        Schema::create('client_contacts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('client_id')->constrained()->cascadeOnDelete();
            $table->string('first_name');
            $table->string('last_name');
            $table->string('email')->nullable();
            $table->string('phone')->nullable();
            $table->string('mobile')->nullable();
            $table->string('job_title')->nullable();
            $table->string('department')->nullable();
            $table->boolean('is_primary')->default(false);
            $table->boolean('is_billing_contact')->default(false);
            $table->boolean('is_technical_contact')->default(false);
            $table->text('notes')->nullable();
            $table->boolean('is_active')->default(true);
            $table->timestamps();
            $table->softDeletes();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('client_contacts');
        Schema::dropIfExists('clients');
    }
};