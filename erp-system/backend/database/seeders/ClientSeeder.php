<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;
use App\Models\Client;
use App\Models\User;

class ClientSeeder extends Seeder
{
    public function run(): void
    {
        $accountManager = User::where('email', 'sales@erp.local')->first();

        $clients = [
            [
                'name' => 'TechCorp Industries',
                'code' => 'TECHCORP',
                'email' => 'contact@techcorp.com',
                'phone' => '+1-555-0100',
                'website' => 'https://techcorp.com',
                'billing_address' => [
                    'line1' => '100 Tech Park Drive',
                    'city' => 'San Francisco',
                    'state' => 'CA',
                    'postal_code' => '94105',
                    'country' => 'USA',
                ],
                'contact_person' => 'John Smith',
                'contact_email' => 'john.smith@techcorp.com',
                'contact_phone' => '+1-555-0101',
                'tax_number' => 'US123456789',
                'payment_terms' => 30,
                'currency' => 'USD',
                'credit_limit' => 500000,
                'account_manager_id' => $accountManager?->id,
                'status' => 'active',
                'industry' => 'Technology',
                'company_size' => '1000+',
            ],
            [
                'name' => 'Global Retail Solutions',
                'code' => 'GRS',
                'email' => 'procurement@globalretail.com',
                'phone' => '+1-555-0200',
                'website' => 'https://globalretail.com',
                'billing_address' => [
                    'line1' => '500 Commerce Blvd',
                    'city' => 'New York',
                    'state' => 'NY',
                    'postal_code' => '10001',
                    'country' => 'USA',
                ],
                'contact_person' => 'Maria Rodriguez',
                'contact_email' => 'maria.rodriguez@globalretail.com',
                'contact_phone' => '+1-555-0201',
                'tax_number' => 'US987654321',
                'payment_terms' => 45,
                'currency' => 'USD',
                'credit_limit' => 750000,
                'account_manager_id' => $accountManager?->id,
                'status' => 'active',
                'industry' => 'Retail',
                'company_size' => '501-1000',
            ],
            [
                'name' => 'Healthcare Partners Inc',
                'code' => 'HPI',
                'email' => 'vendor@healthcarepartners.com',
                'phone' => '+1-555-0300',
                'website' => 'https://healthcarepartners.com',
                'billing_address' => [
                    'line1' => '200 Medical Center Drive',
                    'city' => 'Boston',
                    'state' => 'MA',
                    'postal_code' => '02115',
                    'country' => 'USA',
                ],
                'contact_person' => 'Dr. James Wilson',
                'contact_email' => 'jwilson@healthcarepartners.com',
                'contact_phone' => '+1-555-0301',
                'tax_number' => 'US456789123',
                'payment_terms' => 60,
                'currency' => 'USD',
                'credit_limit' => 1000000,
                'account_manager_id' => $accountManager?->id,
                'status' => 'active',
                'industry' => 'Healthcare',
                'company_size' => '201-500',
            ],
            [
                'name' => 'Financial Services Group',
                'code' => 'FSG',
                'email' => 'it-procurement@fsg.com',
                'phone' => '+1-555-0400',
                'website' => 'https://fsg.com',
                'billing_address' => [
                    'line1' => '1 Wall Street',
                    'city' => 'New York',
                    'state' => 'NY',
                    'postal_code' => '10005',
                    'country' => 'USA',
                ],
                'contact_person' => 'Sarah Thompson',
                'contact_email' => 'sarah.thompson@fsg.com',
                'contact_phone' => '+1-555-0401',
                'tax_number' => 'US789123456',
                'payment_terms' => 30,
                'currency' => 'USD',
                'credit_limit' => 2000000,
                'account_manager_id' => $accountManager?->id,
                'status' => 'active',
                'industry' => 'Financial Services',
                'company_size' => '1000+',
            ],
            [
                'name' => 'StartupXYZ',
                'code' => 'STARTUPXYZ',
                'email' => 'founders@startupxyz.io',
                'phone' => '+1-555-0500',
                'website' => 'https://startupxyz.io',
                'billing_address' => [
                    'line1' => '50 Startup Lane',
                    'city' => 'Austin',
                    'state' => 'TX',
                    'postal_code' => '78701',
                    'country' => 'USA',
                ],
                'contact_person' => 'Alex Chen',
                'contact_email' => 'alex@startupxyz.io',
                'contact_phone' => '+1-555-0501',
                'tax_number' => 'US321654987',
                'payment_terms' => 15,
                'currency' => 'USD',
                'credit_limit' => 50000,
                'account_manager_id' => $accountManager?->id,
                'status' => 'prospect',
                'industry' => 'Technology',
                'company_size' => '1-10',
            ],
        ];

        foreach ($clients as $clientData) {
            $client = Client::firstOrCreate(['code' => $clientData['code']], $clientData);

            // Add contacts
            if ($clientData['contact_person']) {
                $names = explode(' ', $clientData['contact_person']);
                $client->contacts()->firstOrCreate(
                    ['email' => $clientData['contact_email']],
                    [
                        'first_name' => $names[0] ?? $clientData['contact_person'],
                        'last_name' => $names[1] ?? '',
                        'email' => $clientData['contact_email'],
                        'phone' => $clientData['contact_phone'],
                        'job_title' => 'Primary Contact',
                        'is_primary' => true,
                        'is_billing_contact' => true,
                        'is_active' => true,
                    ]
                );
            }
        }
    }
}