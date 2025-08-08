'use server'

import { createClient } from '@/lib/supabase/server'
import { redirect } from 'next/navigation'
import prisma from '@/lib/db' // Import the new Prisma client
import { Profile } from '@prisma/client'
import { JsonValue } from '@prisma/client/runtime/library'

// Action to get user profile from your DB
export async function getProfile() {
  const supabase = createClient()
  const { data: { user }, error } = await supabase.auth.getUser()
  
  // Detailed logging for debugging
  console.log('🔍 getProfile - Auth getUser result:', {
    hasUser: !!user,
    user: user ? {
      id: user.id,
      email: user.email,
      user_metadata: user.user_metadata,
      identities: user.identities,
      app_metadata: user.app_metadata,
      created_at: user.created_at,
      updated_at: user.updated_at
    } : null,
    error: error ? {
      message: error.message,
      status: error.status
    } : null
  })
  
  if (!user) {
    console.log('❌ getProfile - No user found')
    return null
  }
  
  // Try to get email from multiple sources (Fix 2)
  const userEmail = user.email || 
                   user.user_metadata?.email || 
                   user.identities?.[0]?.identity_data?.email ||
                   user.app_metadata?.email

  console.log('🔍 getProfile - Email sources check:', {
    directEmail: user.email,
    metadataEmail: user.user_metadata?.email,
    identityEmail: user.identities?.[0]?.identity_data?.email,
    appMetadataEmail: user.app_metadata?.email,
    finalEmail: userEmail
  })

  if (!userEmail) {
    console.error('❌ getProfile - No email found from any source')
    console.error('Full user object for debugging:', JSON.stringify(user, null, 2))
    return null
  }

  console.log('✅ getProfile - Email resolved:', userEmail)

  try {
    const profile = await prisma.profile.findUnique({
      where: { email: userEmail }, // Use resolved email
    })
    console.log('🔍 getProfile - Database query result:', {
      hasProfile: !!profile,
      profileId: profile?.id,
      profileEmail: profile?.email
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
          where: { email: userEmail }, // Use resolved email
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
  const { data: { user }, error } = await supabase.auth.getUser()
  
  // Detailed logging for debugging
  console.log('🔍 updateProfile - Auth getUser result:', {
    hasUser: !!user,
    user: user ? {
      id: user.id,
      email: user.email,
      user_metadata: user.user_metadata,
      identities: user.identities,
      app_metadata: user.app_metadata,
      created_at: user.created_at,
      updated_at: user.updated_at
    } : null,
    error: error ? {
      message: error.message,
      status: error.status
    } : null,
    formData: {
      full_name: formData.full_name,
      onboarding_completed: formData.onboarding_completed,
      onboarding_presented: formData.onboarding_presented
    }
  })
  
  if (!user) {
    console.error('❌ updateProfile - User not authenticated')
    throw new Error('User not authenticated')
  }
  
  // Try to get email from multiple sources (Fix 2)
  const userEmail = user.email || 
                   user.user_metadata?.email || 
                   user.identities?.[0]?.identity_data?.email ||
                   user.app_metadata?.email

  console.log('🔍 updateProfile - Email sources check:', {
    directEmail: user.email,
    metadataEmail: user.user_metadata?.email,
    identityEmail: user.identities?.[0]?.identity_data?.email,
    appMetadataEmail: user.app_metadata?.email,
    finalEmail: userEmail,
    identitiesCount: user.identities?.length || 0,
    identitiesPreview: user.identities?.map(id => ({
      provider: id.provider,
      hasEmail: !!id.identity_data?.email
    }))
  })

  if (!userEmail) {
    console.error('❌ updateProfile - No email found from any source')
    console.error('Full user object for debugging:', JSON.stringify(user, null, 2))
    throw new Error('User email is required but not available from any source')
  }

  console.log('✅ updateProfile - Email resolved:', userEmail)

  // Create a clean object without any extra fields
  const cleanData = {
    email: userEmail, // Use the resolved email
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
    console.log('🔍 updateProfile - Starting database operations with:', {
      userId: user.id,
      userEmail: userEmail,
      cleanDataKeys: Object.keys(cleanData)
    })
    
    // First, try to find the profile by ID (most reliable for auth)
    console.log('🔍 updateProfile - Looking for profile by ID:', user.id)
    let profile = await prisma.profile.findUnique({
      where: { id: user.id }
    })

    if (profile) {
      console.log('✅ updateProfile - Found profile by ID, updating...')
      // Profile exists by ID, update it
      await prisma.profile.update({
        where: { id: user.id },
        data: { ...cleanData, email: userEmail } // Ensure email is updated too
      })
      console.log('✅ updateProfile - Successfully updated profile by ID')
    } else {
      console.log('🔍 updateProfile - No profile found by ID, checking by email:', userEmail)
      // No profile by ID, check if one exists by email
      profile = await prisma.profile.findUnique({
        where: { email: userEmail }
      })
      
      if (profile) {
        console.log('✅ updateProfile - Found profile by email, updating ID...')
        // Profile exists by email but different ID, update the ID
        await prisma.profile.update({
          where: { email: userEmail },
          data: { ...cleanData, id: user.id }
        })
        console.log('✅ updateProfile - Successfully updated profile by email')
      } else {
        console.log('🆕 updateProfile - No profile found, creating new one...')
        // No profile exists, create a new one
        await prisma.profile.create({
          data: { ...cleanData, id: user.id, email: userEmail }
        })
        console.log('✅ updateProfile - Successfully created new profile')
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
            data: { ...cleanData, email: userEmail }
          })
        } else {
          profile = await prisma.profile.findUnique({
            where: { email: userEmail }
          })
          
          if (profile) {
            await prisma.profile.update({
              where: { email: userEmail },
              data: { ...cleanData, id: user.id }
            })
          } else {
            await prisma.profile.create({
              data: { ...cleanData, id: user.id, email: userEmail }
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
    if (!user) return null

    // Try to get email from multiple sources (Fix 2)
    const userEmail = user.email || 
                     user.user_metadata?.email || 
                     user.identities?.[0]?.identity_data?.email ||
                     user.app_metadata?.email

    if (!userEmail) return null

    try {
        const student = await prisma.student.findUnique({
            where: { email: userEmail }
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
                    where: { email: userEmail }
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