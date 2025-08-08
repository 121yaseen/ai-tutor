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

  try {
    const profile = await prisma.profile.findUnique({
      where: { email: user.email },
    })
    return profile
  } catch (error) {
    console.error('Error fetching profile:', error)
    // Retry once if it's a connection or prepared statement issue
    if (error instanceof Error && (
      error.message.includes('prepared statement') || 
      error.message.includes('Connection') ||
      error.message.includes('pool')
    )) {
      try {
        await prisma.$disconnect()
        await new Promise(resolve => setTimeout(resolve, 100)) // Small delay
        const profile = await prisma.profile.findUnique({
          where: { email: user.email },
        })
        return profile
      } catch (retryError) {
        console.error('Retry failed:', retryError)
        throw retryError
      }
    }
    throw error
  }
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

  try {
    // First, try to find the profile by ID (most reliable for auth)
    let profile = await prisma.profile.findUnique({
      where: { id: user.id }
    })

    if (profile) {
      // Profile exists by ID, update it
      await prisma.profile.update({
        where: { id: user.id },
        data: { ...cleanData, email: user.email } // Ensure email is updated too
      })
    } else {
      // No profile by ID, check if one exists by email
      profile = await prisma.profile.findUnique({
        where: { email: user.email }
      })
      
      if (profile) {
        // Profile exists by email but different ID, update the ID
        await prisma.profile.update({
          where: { email: user.email },
          data: { ...cleanData, id: user.id }
        })
      } else {
        // No profile exists, create a new one
        await prisma.profile.create({
          data: { ...cleanData, id: user.id, email: user.email }
        })
      }
    }
  } catch (error) {
    console.error('Error updating profile:', error)
    // Retry once if it's a connection or prepared statement issue
    if (error instanceof Error && (
      error.message.includes('prepared statement') || 
      error.message.includes('Connection') ||
      error.message.includes('pool')
    )) {
      try {
        await prisma.$disconnect()
        await new Promise(resolve => setTimeout(resolve, 100)) // Small delay
        
        // Retry with the same logic
        let profile = await prisma.profile.findUnique({
          where: { id: user.id }
        })

        if (profile) {
          await prisma.profile.update({
            where: { id: user.id },
            data: { ...cleanData, email: user.email }
          })
        } else {
          profile = await prisma.profile.findUnique({
            where: { email: user.email }
          })
          
          if (profile) {
            await prisma.profile.update({
              where: { email: user.email },
              data: { ...cleanData, id: user.id }
            })
          } else {
            await prisma.profile.create({
              data: { ...cleanData, id: user.id, email: user.email }
            })
          }
        }
      } catch (retryError) {
        console.error('Retry failed:', retryError)
        throw retryError
      }
    } else {
      throw error
    }
  }
}

// Action to get student history from your DB
export async function getStudentHistory(): Promise<JsonValue[] | null> {
    const supabase = createClient()
    const { data: { user } } = await supabase.auth.getUser()
    if (!user || !user.email) return null

    try {
        const student = await prisma.student.findUnique({
            where: { email: user.email }
        });
        return student?.history ? student.history as JsonValue[] : [];
    } catch (error) {
        console.error('Error fetching student history:', error)
        // Retry once if it's a connection or prepared statement issue
        if (error instanceof Error && (
            error.message.includes('prepared statement') || 
            error.message.includes('Connection') ||
            error.message.includes('pool')
        )) {
            try {
                await prisma.$disconnect()
                await new Promise(resolve => setTimeout(resolve, 100)) // Small delay
                const student = await prisma.student.findUnique({
                    where: { email: user.email }
                });
                return student?.history ? student.history as JsonValue[] : [];
            } catch (retryError) {
                console.error('Retry failed:', retryError)
                throw retryError
            }
        }
        throw error
    }
}

// The signOutAction remains the same as it's purely for auth
export async function signOutAction() {
  const supabase = createClient()
  await supabase.auth.signOut()
  redirect('/login')
} 