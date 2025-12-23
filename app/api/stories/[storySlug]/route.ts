import { type NextRequest, NextResponse } from "next/server";
import { getStoryWithPagesBySlug } from "@/lib/db-actions";
import { db } from "@/lib/db";
import { stories } from "@/lib/schema";

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ storySlug: string }> }
) {
  try {
    const { storySlug: slug } = await params;
    console.log("API: Fetching story with slug:", slug);

    // Special case: if slug is "all", return all stories for debugging
    if (slug === "all") {
      const allStories = await db.select().from(stories);
      return NextResponse.json({
        message: "All stories",
        stories: allStories.map(s => ({ id: s.id, slug: s.slug, title: s.title }))
      });
    }

    if (!slug) {
      return NextResponse.json(
        { error: "Story slug is required" },
        { status: 400 }
      );
    }

    const result = await getStoryWithPagesBySlug(slug);
    console.log("API: Result found:", !!result);

    if (!result) {
      return NextResponse.json(
        { error: "Story not found" },
        { status: 404 }
      );
    }

    return NextResponse.json(result);
  } catch (error) {
    console.error("Error fetching story:", error);
    return NextResponse.json(
      { error: "Failed to fetch story" },
      { status: 500 }
    );
  }
}