<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Project;
use App\Models\Client;
use App\Models\User;
use App\Models\Department;

class ProjectSeeder extends Seeder
{
    public function run(): void
    {
        $techcorp = Client::where('code', 'TECHCORP')->first();
        $grs = Client::where('code', 'GRS')->first();
        $hpi = Client::where('code', 'HPI')->first();
        $fsg = Client::where('code', 'FSG')->first();

        $pm1 = User::where('email', 'pm1@erp.local')->first();
        $pm2 = User::where('email', 'pm2@erp.local')->first();

        $engDept = Department::where('code', 'ENG')->first();
        $desDept = Department::where('code', 'DES')->first();

        $seniorDevs = User::whereHas('roles', fn($q) => $q->where('name', 'Senior Consultant'))->get();
        $consultants = User::whereHas('roles', fn($q) => $q->where('name', 'Consultant'))->get();

        $projects = [
            [
                'name' => 'TechCorp Platform Modernization',
                'code' => 'TC-PM-2024',
                'description' => 'Complete modernization of legacy platform to microservices architecture',
                'client_id' => $techcorp?->id,
                'department_id' => $engDept?->id,
                'project_manager_id' => $pm1?->id,
                'status' => 'active',
                'priority' => 'high',
                'start_date' => now()->subMonths(3),
                'end_date' => now()->addMonths(6),
                'estimated_hours' => 4800,
                'estimated_budget' => 720000,
                'billing_type' => 'time_material',
                'hourly_rate' => 150,
                'currency' => 'USD',
                'is_billable' => true,
            ],
            [
                'name' => 'TechCorp Mobile App Development',
                'code' => 'TC-MOB-2024',
                'description' => 'Native iOS and Android app for customer portal',
                'client_id' => $techcorp?->id,
                'department_id' => $engDept?->id,
                'project_manager_id' => $pm1?->id,
                'status' => 'active',
                'priority' => 'medium',
                'start_date' => now()->subMonth(1),
                'end_date' => now()->addMonths(4),
                'estimated_hours' => 2400,
                'estimated_budget' => 360000,
                'billing_type' => 'fixed_price',
                'fixed_price' => 360000,
                'currency' => 'USD',
                'is_billable' => true,
            ],
            [
                'name' => 'GRS E-commerce Platform Redesign',
                'code' => 'GRS-ECOM-2024',
                'description' => 'Complete redesign of e-commerce platform with new UI/UX',
                'client_id' => $grs?->id,
                'department_id' => $desDept?->id,
                'project_manager_id' => $pm2?->id,
                'status' => 'active',
                'priority' => 'high',
                'start_date' => now()->subMonths(2),
                'end_date' => now()->addMonths(3),
                'estimated_hours' => 1800,
                'estimated_budget' => 270000,
                'billing_type' => 'time_material',
                'hourly_rate' => 150,
                'currency' => 'USD',
                'is_billable' => true,
            ],
            [
                'name' => 'HPI Patient Portal Development',
                'code' => 'HPI-PORTAL-2024',
                'description' => 'HIPAA-compliant patient portal with appointment scheduling',
                'client_id' => $hpi?->id,
                'department_id' => $engDept?->id,
                'project_manager_id' => $pm1?->id,
                'status' => 'planning',
                'priority' => 'critical',
                'start_date' => now()->addMonth(1),
                'end_date' => now()->addMonths(8),
                'estimated_hours' => 3200,
                'estimated_budget' => 480000,
                'billing_type' => 'milestone',
                'hourly_rate' => 150,
                'currency' => 'USD',
                'is_billable' => true,
            ],
            [
                'name' => 'FSG Trading Dashboard',
                'code' => 'FSG-TD-2024',
                'description' => 'Real-time trading dashboard with analytics',
                'client_id' => $fsg?->id,
                'department_id' => $engDept?->id,
                'project_manager_id' => $pm1?->id,
                'status' => 'active',
                'priority' => 'critical',
                'start_date' => now()->subMonths(4),
                'end_date' => now()->addMonths(2),
                'estimated_hours' => 2000,
                'estimated_budget' => 400000,
                'billing_type' => 'time_material',
                'hourly_rate' => 200,
                'currency' => 'USD',
                'is_billable' => true,
            ],
            [
                'name' => 'Internal HR System Upgrade',
                'code' => 'INT-HR-2024',
                'description' => 'Upgrade internal HR management system',
                'client_id' => null,
                'department_id' => $engDept?->id,
                'project_manager_id' => $pm2?->id,
                'status' => 'on_hold',
                'priority' => 'low',
                'start_date' => now()->subMonths(1),
                'end_date' => now()->addMonths(3),
                'estimated_hours' => 800,
                'estimated_budget' => 120000,
                'billing_type' => 'time_material',
                'hourly_rate' => 150,
                'currency' => 'USD',
                'is_billable' => false,
            ],
        ];

        foreach ($projects as $projectData) {
            $project = Project::firstOrCreate(['code' => $projectData['code']], $projectData);

            // Add project members
            if ($pm1) {
                $project->members()->syncWithoutDetaching([
                    $pm1->id => [
                        'role' => 'manager',
                        'hourly_rate' => 150,
                        'allocated_hours' => 40,
                        'start_date' => $projectData['start_date'],
                    ],
                ]);
            }
            if ($pm2) {
                $project->members()->syncWithoutDetaching([
                    $pm2->id => [
                        'role' => 'manager',
                        'hourly_rate' => 140,
                        'allocated_hours' => 40,
                        'start_date' => $projectData['start_date'],
                    ],
                ]);
            }

            // Add senior developers and consultants
            foreach ($seniorDevs->take(2) as $dev) {
                $project->members()->syncWithoutDetaching([
                    $dev->id => [
                        'role' => 'member',
                        'hourly_rate' => $dev->hourly_rate,
                        'allocated_hours' => 30,
                        'start_date' => $projectData['start_date'],
                    ],
                ]);
            }

            foreach ($consultants->take(3) as $dev) {
                $project->members()->syncWithoutDetaching([
                    $dev->id => [
                        'role' => 'member',
                        'hourly_rate' => $dev->hourly_rate,
                        'allocated_hours' => 20,
                        'start_date' => $projectData['start_date'],
                    ],
                ]);
            }
        }
    }
}