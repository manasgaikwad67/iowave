<?php

namespace App\Http\Controllers\Api\Auth;

use App\Http\Controllers\Api\BaseController;
use App\Http\Requests\Auth\LoginRequest;
use App\Http\Requests\Auth\RegisterRequest;
use App\Http\Requests\Auth\ForgotPasswordRequest;
use App\Http\Requests\Auth\ResetPasswordRequest;
use App\Http\Resources\UserResource;
use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Password;
use Illuminate\Validation\ValidationException;

class AuthController extends BaseController
{
    public function login(LoginRequest $request): JsonResponse
    {
        $credentials = $request->only('email', 'password');

        if (!Auth::attempt($credentials, $request->boolean('remember'))) {
            throw ValidationException::withMessages([
                'email' => ['The provided credentials are incorrect.'],
            ]);
        }

        $user = Auth::user();
        $user->update(['last_login_at' => now()]);

        $token = $user->createToken('api-token', ['*'])->plainTextToken;

        return $this->success([
            'user' => new UserResource($user->load('roles', 'permissions', 'department')),
            'token' => $token,
            'token_type' => 'Bearer',
        ], 'Login successful');
    }

    public function register(RegisterRequest $request): JsonResponse
    {
        $user = User::create($request->validated());
        $user->assignRole('Consultant');

        $token = $user->createToken('api-token', ['*'])->plainTextToken;

        return $this->created([
            'user' => new UserResource($user->load('roles', 'permissions', 'department')),
            'token' => $token,
            'token_type' => 'Bearer',
        ], 'Registration successful');
    }

    public function logout(Request $request): JsonResponse
    {
        $request->user()->currentAccessToken()->delete();

        return $this->success(null, 'Logged out successfully');
    }

    public function me(Request $request): JsonResponse
    {
        return $this->success(
            new UserResource($request->user()->load('roles', 'permissions', 'department', 'manager'))
        );
    }

    public function forgotPassword(ForgotPasswordRequest $request): JsonResponse
    {
        $status = Password::sendResetLink($request->only('email'));

        return $status === Password::RESET_LINK_SENT
            ? $this->success(null, 'Password reset link sent to your email')
            : $this->error('Unable to send reset link', 400);
    }

    public function resetPassword(ResetPasswordRequest $request): JsonResponse
    {
        $status = Password::reset(
            $request->only('email', 'password', 'password_confirmation', 'token'),
            function (User $user, string $password) {
                $user->forceFill([
                    'password' => Hash::make($password),
                ])->setRememberToken(\Str::random(60));
                $user->save();
            }
        );

        return $status === Password::PASSWORD_RESET
            ? $this->success(null, 'Password has been reset')
            : $this->error('Unable to reset password', 400);
    }

    public function updateProfile(Request $request): JsonResponse
    {
        $user = $request->user();
        $user->update($request->validate([
            'first_name' => 'sometimes|string|max:255',
            'last_name' => 'sometimes|string|max:255',
            'phone' => 'sometimes|nullable|string|max:255',
            'timezone' => 'sometimes|string|max:50',
            'locale' => 'sometimes|string|max:10',
        ]));

        return $this->success(new UserResource($user->load('roles', 'permissions', 'department')));
    }

    public function updatePassword(Request $request): JsonResponse
    {
        $request->validate([
            'current_password' => 'required|string',
            'password' => 'required|string|min:8|confirmed',
        ]);

        $user = $request->user();

        if (!Hash::check($request->current_password, $user->password)) {
            return $this->error('Current password is incorrect', 400);
        }

        $user->update(['password' => Hash::make($request->password)]);

        return $this->success(null, 'Password updated successfully');
    }
}