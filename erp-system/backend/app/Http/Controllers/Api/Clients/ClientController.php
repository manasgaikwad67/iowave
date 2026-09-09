<?php

namespace App\Http\Controllers\Api\Clients;

use App\Http\Controllers\Api\BaseController;
use App\Http\Requests\Clients\StoreClientRequest;
use App\Http\Requests\Clients\UpdateClientRequest;
use App\Http\Resources\ClientResource;
use App\Models\Client;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class ClientController extends BaseController
{
    public function index(Request $request): JsonResponse
    {
        $query = Client::with(['accountManager', 'contacts'])
            ->when($request->search, fn($q) => $q->where('name', 'like', "%{$request->search}%")
                ->orWhere('code', 'like', "%{$request->search}%")
                ->orWhere('email', 'like', "%{$request->search}%"))
            ->when($request->status, fn($q) => $q->where('status', $request->status))
            ->when($request->account_manager_id, fn($q) => $q->where('account_manager_id', $request->account_manager_id))
            ->when($request->is_active !== null, fn($q) => $q->where('is_active', $request->boolean('is_active')));

        $clients = $query->orderBy($request->sort ?? 'name')
            ->paginate($request->per_page ?? 15);

        return $this->paginated($clients, ClientResource::class);
    }

    public function store(StoreClientRequest $request): JsonResponse
    {
        $client = Client::create($request->validated());

        return $this->created(new ClientResource($client->load(['accountManager', 'contacts'])));
    }

    public function show(Request $request, Client $client): JsonResponse
    {
        return $this->success(new ClientResource($client->load(['accountManager', 'contacts', 'projects'])));
    }

    public function update(UpdateClientRequest $request, Client $client): JsonResponse
    {
        $client->update($request->validated());

        return $this->success(new ClientResource($client->load(['accountManager', 'contacts'])));
    }

    public function destroy(Client $client): JsonResponse
    {
        $client->delete();
        return $this->noContent();
    }

    public function contacts(Request $request, Client $client): JsonResponse
    {
        $contacts = $client->contacts()->paginate($request->per_page ?? 15);
        return $this->paginated($contacts, \App\Http\Resources\ClientContactResource::class);
    }
}