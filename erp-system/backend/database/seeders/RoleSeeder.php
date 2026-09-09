<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use Spatie\Permission\Models\Role;

class RoleSeeder extends Seeder
{
    public function run(): void
    {
        $roles = [
            'Super Admin' => [
                'description' => 'Full system access',
                'permissions' => '*',
            ],
            'Admin' => [
                'description' => 'Administrative access',
                'permissions' => [
                    'users.*',
                    'departments.*',
                    'clients.*',
                    'projects.*',
                    'tasks.*',
                    'time_entries.*',
                    'invoices.*',
                    'payments.*',
                    'expenses.*',
                    'reports.*',
                    'settings.*',
                ],
            ],
            'Project Manager' => [
                'description' => 'Manage projects and teams',
                'permissions' => [
                    'users.view',
                    'departments.view',
                    'clients.view',
                    'clients.create',
                    'clients.edit',
                    'projects.*',
                    'tasks.*',
                    'time_entries.view',
                    'time_entries.create',
                    'time_entries.edit',
                    'time_entries.approve',
                    'time_entries.view_all',
                    'invoices.view',
                    'invoices.create',
                    'invoices.edit',
                    'invoices.send',
                    'expenses.view',
                    'expenses.create',
                    'expenses.edit',
                    'expenses.approve',
                    'reports.view',
                    'reports.project_profitability',
                ],
            ],
            'Team Lead' => [
                'description' => 'Lead a team within projects',
                'permissions' => [
                    'users.view',
                    'projects.view',
                    'tasks.*',
                    'time_entries.view',
                    'time_entries.create',
                    'time_entries.edit',
                    'time_entries.approve',
                    'reports.view',
                    'reports.utilization',
                ],
            ],
            'Senior Consultant' => [
                'description' => 'Senior billable resource',
                'permissions' => [
                    'projects.view',
                    'tasks.view',
                    'tasks.update_status',
                    'time_entries.view',
                    'time_entries.create',
                    'time_entries.edit',
                    'expenses.view',
                    'expenses.create',
                    'expenses.edit',
                ],
            ],
            'Consultant' => [
                'description' => 'Billable resource',
                'permissions' => [
                    'projects.view',
                    'tasks.view',
                    'tasks.update_status',
                    'time_entries.view',
                    'time_entries.create',
                    'time_entries.edit',
                    'expenses.view',
                    'expenses.create',
                    'expenses.edit',
                ],
            ],
            'Client' => [
                'description' => 'Client portal access',
                'permissions' => [
                    'projects.view',
                    'tasks.view',
                    'invoices.view',
                    'time_entries.view',
                ],
            ],
        ];

        foreach ($roles as $name => $data) {
            $role = Role::firstOrCreate(['name' => $name, 'guard_name' => 'api']);
            
            if ($data['permissions'] === '*') {
                $role->syncPermissions(\Spatie\Permission\Models\Permission::all());
            } else {
                $permissions = [];
                foreach ($data['permissions'] as $perm) {
                    if (str_ends_with($perm, '.*')) {
                        $prefix = rtrim($perm, '.*');
                        $permissions = array_merge($permissions, 
                            \Spatie\Permission\Models\Permission::where('name', 'like', $prefix . '.%')->pluck('name')->toArray()
                        );
                    } else {
                        $permissions[] = $perm;
                    }
                }
                $role->syncPermissions($permissions);
            }
        }
    }
}