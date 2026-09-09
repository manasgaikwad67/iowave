<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\User;
use App\Models\Department;
use Spatie\Permission\Models\Role;

class UserSeeder extends Seeder
{
    public function run(): void
    {
        // Create departments first
        $engineering = Department::firstOrCreate(
            ['code' => 'ENG'],
            ['name' => 'Engineering', 'description' => 'Software Engineering Department']
        );

        $design = Department::firstOrCreate(
            ['code' => 'DES'],
            ['name' => 'Design', 'description' => 'UI/UX Design Department']
        );

        $sales = Department::firstOrCreate(
            ['code' => 'SAL'],
            ['name' => 'Sales', 'description' => 'Sales & Business Development']
        );

        $finance = Department::firstOrCreate(
            ['code' => 'FIN'],
            ['name' => 'Finance', 'description' => 'Finance & Accounting']
        );

        // Create Super Admin
        $superAdmin = User::firstOrCreate(
            ['email' => 'admin@erp.local'],
            [
                'first_name' => 'Super',
                'last_name' => 'Admin',
                'password' => bcrypt('password123'),
                'job_title' => 'System Administrator',
                'department_id' => $engineering->id,
                'is_active' => true,
                'email_verified_at' => now(),
            ]
        );
        $superAdmin->assignRole('Super Admin');

        // Create Admin
        $admin = User::firstOrCreate(
            ['email' => 'admin2@erp.local'],
            [
                'first_name' => 'Admin',
                'last_name' => 'User',
                'password' => bcrypt('password123'),
                'job_title' => 'Administrator',
                'department_id' => $engineering->id,
                'is_active' => true,
                'email_verified_at' => now(),
            ]
        );
        $admin->assignRole('Admin');

        // Create Project Managers
        $pm1 = User::firstOrCreate(
            ['email' => 'pm1@erp.local'],
            [
                'first_name' => 'Sarah',
                'last_name' => 'Johnson',
                'password' => bcrypt('password123'),
                'job_title' => 'Senior Project Manager',
                'department_id' => $engineering->id,
                'hourly_rate' => 150,
                'is_active' => true,
                'email_verified_at' => now(),
            ]
        );
        $pm1->assignRole('Project Manager');

        $pm2 = User::firstOrCreate(
            ['email' => 'pm2@erp.local'],
            [
                'first_name' => 'Michael',
                'last_name' => 'Chen',
                'password' => bcrypt('password123'),
                'job_title' => 'Project Manager',
                'department_id' => $design->id,
                'hourly_rate' => 140,
                'is_active' => true,
                'email_verified_at' => now(),
            ]
        );
        $pm2->assignRole('Project Manager');

        // Create Team Leads
        $tl1 = User::firstOrCreate(
            ['email' => 'tl1@erp.local'],
            [
                'first_name' => 'Emily',
                'last_name' => 'Davis',
                'password' => bcrypt('password123'),
                'job_title' => 'Engineering Team Lead',
                'department_id' => $engineering->id,
                'manager_id' => $pm1->id,
                'hourly_rate' => 120,
                'is_active' => true,
                'email_verified_at' => now(),
            ]
        );
        $tl1->assignRole('Team Lead');

        $tl2 = User::firstOrCreate(
            ['email' => 'tl2@erp.local'],
            [
                'first_name' => 'James',
                'last_name' => 'Wilson',
                'password' => bcrypt('password123'),
                'job_title' => 'Design Team Lead',
                'department_id' => $design->id,
                'manager_id' => $pm2->id,
                'hourly_rate' => 115,
                'is_active' => true,
                'email_verified_at' => now(),
            ]
        );
        $tl2->assignRole('Team Lead');

        // Create Senior Consultants
        $sc1 = User::firstOrCreate(
            ['email' => 'sc1@erp.local'],
            [
                'first_name' => 'Lisa',
                'last_name' => 'Anderson',
                'password' => bcrypt('password123'),
                'job_title' => 'Senior Backend Developer',
                'department_id' => $engineering->id,
                'manager_id' => $tl1->id,
                'hourly_rate' => 110,
                'is_active' => true,
                'email_verified_at' => now(),
            ]
        );
        $sc1->assignRole('Senior Consultant');

        $sc2 = User::firstOrCreate(
            ['email' => 'sc2@erp.local'],
            [
                'first_name' => 'David',
                'last_name' => 'Martinez',
                'password' => bcrypt('password123'),
                'job_title' => 'Senior Frontend Developer',
                'department_id' => $engineering->id,
                'manager_id' => $tl1->id,
                'hourly_rate' => 105,
                'is_active' => true,
                'email_verified_at' => now(),
            ]
        );
        $sc2->assignRole('Senior Consultant');

        // Create Consultants
        $consultants = [
            ['email' => 'dev1@erp.local', 'first_name' => 'Alex', 'last_name' => 'Thompson', 'job_title' => 'Backend Developer', 'department_id' => $engineering->id, 'manager_id' => $tl1->id, 'hourly_rate' => 90],
            ['email' => 'dev2@erp.local', 'first_name' => 'Maria', 'last_name' => 'Garcia', 'job_title' => 'Frontend Developer', 'department_id' => $engineering->id, 'manager_id' => $tl1->id, 'hourly_rate' => 85],
            ['email' => 'dev3@erp.local', 'first_name' => 'Kevin', 'last_name' => 'Lee', 'job_title' => 'Full Stack Developer', 'department_id' => $engineering->id, 'manager_id' => $tl1->id, 'hourly_rate' => 95],
            ['email' => 'des1@erp.local', 'first_name' => 'Amanda', 'last_name' => 'White', 'job_title' => 'UI/UX Designer', 'department_id' => $design->id, 'manager_id' => $tl2->id, 'hourly_rate' => 85],
            ['email' => 'des2@erp.local', 'first_name' => 'Chris', 'last_name' => 'Brown', 'job_title' => 'Product Designer', 'department_id' => $design->id, 'manager_id' => $tl2->id, 'hourly_rate' => 80],
        ];

        foreach ($consultants as $data) {
            $user = User::firstOrCreate(
                ['email' => $data['email']],
                array_merge($data, [
                    'password' => bcrypt('password123'),
                    'is_active' => true,
                    'email_verified_at' => now(),
                ])
            );
            $user->assignRole('Consultant');
        }

        // Create Sales
        $salesUser = User::firstOrCreate(
            ['email' => 'sales@erp.local'],
            [
                'first_name' => 'Jennifer',
                'last_name' => 'Taylor',
                'password' => bcrypt('password123'),
                'job_title' => 'Account Executive',
                'department_id' => $sales->id,
                'hourly_rate' => 100,
                'is_active' => true,
                'email_verified_at' => now(),
            ]
        );
        $salesUser->assignRole('Senior Consultant');

        // Create Finance
        $financeUser = User::firstOrCreate(
            ['email' => 'finance@erp.local'],
            [
                'first_name' => 'Robert',
                'last_name' => 'Miller',
                'password' => bcrypt('password123'),
                'job_title' => 'Finance Manager',
                'department_id' => $finance->id,
                'hourly_rate' => 130,
                'is_active' => true,
                'email_verified_at' => now(),
            ]
        );
        $financeUser->assignRole('Admin');
    }
}