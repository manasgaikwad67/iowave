<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return ['message' => 'ERP System API'];
});

Route::get('/up', function () {
    return ['status' => 'ok'];
});
