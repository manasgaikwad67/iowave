<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class DocumentResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id,
            'uploaded_by' => $this->whenLoaded('uploader', fn() => new UserResource($this->uploader)),
            'filename' => $this->filename,
            'original_name' => $this->original_name,
            'mime_type' => $this->mime_type,
            'size' => $this->size,
            'formatted_size' => $this->formatted_size,
            'url' => $this->url,
            'category' => $this->category,
            'description' => $this->description,
            'is_public' => $this->is_public,
            'version' => $this->version,
            'created_at' => $this->created_at?->toISOString(),
            'updated_at' => $this->updated_at?->toISOString(),
        ];
    }
}