<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Spatie\Permission\Models\Permission;

class PermissionSeeder extends Seeder
{
    public function run(): void
    {
        $permissions = [
            // User Management
            'users.view',
            'users.create',
            'users.edit',
            'users.delete',
            'users.manage_roles',

            // Department Management
            'departments.view',
            'departments.create',
            'departments.edit',
            'departments.delete',

            // Client Management
            'clients.view',
            'clients.create',
            'clients.edit',
            'clients.delete',
            'clients.manage_contacts',

            // Project Management
            'projects.view',
            'projects.create',
            'projects.edit',
            'projects.delete',
            'projects.manage_members',
            'projects.view_all',
            'projects.manage_budget',

            // Task Management
            'tasks.view',
            'tasks.create',
            'tasks.edit',
            'tasks.delete',
            'tasks.assign',
            'tasks.update_status',

            // Time Tracking
            'time_entries.view',
            'time_entries.create',
            'time_entries.edit',
            'time_entries.delete',
            'time_entries.approve',
            'time_entries.view_all',
            'time_entries.export',

            // Billing & Invoicing
            'invoices.view',
            'invoices.create',
            'invoices.edit',
            'invoices.delete',
            'invoices.send',
            'invoices.view_all',
            'payments.view',
            'payments.create',
            'payments.process',
            'expenses.view',
            'expenses.create',
            'expenses.edit',
            'expenses.delete',
            'expenses.approve',

            // Reports
            'reports.view',
            'reports.export',
            'reports.financial',
            'reports.utilization',
            'reports.project_profitability',

            // Settings
            'settings.view',
            'settings.edit',
        ];

        foreach ($permissions as $permission) {
            Permission::firstOrCreate(['name' => $permission, 'guard_name' => 'api']);
        }
    }
}