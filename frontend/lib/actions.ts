'use server'

import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import prisma from '@/lib/db' // Import the new Prisma client
import { Profile } from '@prisma/client'
import { JsonValue } from '@prisma/client/runtime/library'

// Action to get user profile from your DB
export async function getProfile() {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user || !user.email) return null

  const profile = await prisma.profile.findUnique({
    where: { email: user.email },
  })
  return profile
}

// Action to update the profile in your DB
export async function updateProfile(formData: Partial<Profile>) {
  const supabase = createClient()
  const { data: { user } } = await supabase.auth.getUser()
  if (!user || !user.email) throw new Error('User not authenticated or missing email')

  // Create a clean object without any extra fields
  const cleanData = {
    email: user.email,
    first_name: formData.first_name,
    last_name: formData.last_name,
    full_name: formData.full_name,
    phone_number: formData.phone_number,
    preparing_for: formData.preparing_for,
    previously_attempted_exam: formData.previously_attempted_exam,
    previous_band_score: formData.previous_band_score,
    exam_date: formData.exam_date,
    target_band_score: formData.target_band_score,
    country: formData.country,
    native_language: formData.native_language,
    onboarding_completed: formData.onboarding_completed,
    onboarding_presented: formData.onboarding_presented,
  }

  await prisma.profile.upsert({
    where: { email: user.email },
    update: cleanData,
    create: { ...cleanData, id: user.id, email: user.email },
  })
}

// Action to get student history from your DB
export async function getStudentHistory(): Promise<JsonValue[] | null> {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()
    if (!user || !user.email) return null

    const student = await prisma.student.findUnique({
        where: { email: user.email }
    });
    return student?.history ? student.history as JsonValue[] : [];
}

// The signOutAction remains the same as it's purely for auth
export async function signOutAction() {
  const supabase = createClient()
  await supabase.auth.signOut()
  redirect('/login')
} 