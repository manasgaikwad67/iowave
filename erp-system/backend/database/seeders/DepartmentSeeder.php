<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Department;
use App\Models\User;

class DepartmentSeeder extends Seeder
{
    public function run(): void
    {
        $departments = [
            [
                'name' => 'Engineering',
                'code' => 'ENG',
                'description' => 'Software Engineering Department',
                'cost_center' => 'CC-ENG-001',
                'budget' => 2500000,
            ],
            [
                'name' => 'Design',
                'code' => 'DES',
                'description' => 'UI/UX Design Department',
                'cost_center' => 'CC-DES-001',
                'budget' => 800000,
            ],
            [
                'name' => 'Sales & Business Development',
                'code' => 'SAL',
                'description' => 'Sales and Business Development',
                'cost_center' => 'CC-SAL-001',
                'budget' => 1200000,
            ],
            [
                'name' => 'Finance & Accounting',
                'code' => 'FIN',
                'description' => 'Finance and Accounting Department',
                'cost_center' => 'CC-FIN-001',
                'budget' => 600000,
            ],
            [
                'name' => 'Human Resources',
                'code' => 'HR',
                'description' => 'Human Resources Department',
                'cost_center' => 'CC-HR-001',
                'budget' => 400000,
            ],
            [
                'name' => 'Marketing',
                'code' => 'MKT',
                'description' => 'Marketing Department',
                'cost_center' => 'CC-MKT-001',
                'budget' => 700000,
            ],
            [
                'name' => 'Operations',
                'code' => 'OPS',
                'description' => 'Operations Department',
                'cost_center' => 'CC-OPS-001',
                'budget' => 500000,
            ],
        ];

        foreach ($departments as $dept) {
            Department::firstOrCreate(['code' => $dept['code']], $dept);
        }

        // Set managers
        $engManager = User::where('email', 'pm1@erp.local')->first();
        $desManager = User::where('email', 'pm2@erp.local')->first();
        $finManager = User::where('email', 'finance@erp.local')->first();

        if ($engManager) {
            Department::where('code', 'ENG')->update(['manager_id' => $engManager->id]);
        }
        if ($desManager) {
            Department::where('code', 'DES')->update(['manager_id' => $desManager->id]);
        }
        if ($finManager) {
            Department::where('code', 'FIN')->update(['manager_id' => $finManager->id]);
        }
    }
}