"""
Example: Using Langbase Workflow for multi-step AI operations.

This example demonstrates how to use the Workflow class to orchestrate
complex multi-step AI operations with retry logic, timeouts, and error handling.
"""

import asyncio
import os

from dotenv import load_dotenv

from langbase import Langbase, Workflow

load_dotenv()


async def main():
    """
    Demonstrate various workflow capabilities with Langbase operations.
    """
    print("🚀 Langbase Workflow Example")
    print("=" * 50)

    langbase_api_key = os.environ.get("LANGBASE_API_KEY")
    llm_api_key = os.environ.get("LLM_API_KEY")

    if not langbase_api_key:
        print("❌ Missing LANGBASE_API_KEY in environment variables.")
        exit(1)

    if not llm_api_key:
        print("❌ Missing LLM_API_KEY in environment variables.")
        print("Please set: export LLM_API_KEY='your_llm_api_key'")
        exit(1)

    # Initialize Langbase client and Workflow
    langbase = Langbase(api_key=langbase_api_key)
    workflow = Workflow(debug=True)  # Enable debug mode for visibility

    # Example 1: Basic step execution
    print("\n📝 Example 1: Basic Step Execution")
    print("-" * 30)

    async def generate_summary():
        """Generate a summary using Langbase."""
        response = langbase.agent.run(
            input="Summarize the benefits of AI in healthcare.",
            model="openai:gpt-4o-mini",
            api_key=os.environ.get("LLM_API_KEY"),
        )
        return response["output"]

    try:
        summary = await workflow.step(
            {"id": "generate_summary", "run": generate_summary}
        )
        print(f"✅ Summary generated: {summary[:100]}...")
    except Exception as e:
        print(f"❌ Failed to generate summary: {e}")

    # Example 2: Step with timeout
    print("\n⏰ Example 2: Step with Timeout")
    print("-" * 30)

    async def generate_with_timeout():
        """Generate content with potential timeout."""
        response = langbase.agent.run(
            input="Write a detailed story about space exploration.",
            model="openai:gpt-4o-mini",
            api_key=os.environ.get("LLM_API_KEY"),
        )
        return response["output"]

    try:
        story = await workflow.step(
            {
                "id": "generate_story",
                "timeout": 10000,  # 10 seconds timeout
                "run": generate_with_timeout,
            }
        )
        print(f"✅ Story generated: {story[:100]}...")
    except Exception as e:
        print(f"❌ Story generation failed or timed out: {e}")

    # Example 3: Step with retry logic
    print("\n🔄 Example 3: Step with Retry Logic")
    print("-" * 30)

    async def flaky_operation():
        """Simulate a potentially flaky operation."""
        import random

        # Simulate 70% success rate
        if random.random() < 0.7:
            response = langbase.agent.run(
                input="Analyze the impact of renewable energy.",
                model="openai:gpt-4o-mini",
                api_key=os.environ.get("LLM_API_KEY"),
            )
            return response["output"]
        raise Exception("Temporary service unavailable")

    try:
        analysis = await workflow.step(
            {
                "id": "generate_analysis",
                "retries": {
                    "limit": 3,
                    "delay": 1000,  # 1 second delay
                    "backoff": "exponential",
                },
                "run": flaky_operation,
            }
        )
        print(f"✅ Analysis generated: {analysis[:100]}...")
    except Exception as e:
        print(f"❌ Analysis generation failed after retries: {e}")

    # Example 4: Multi-step workflow with dependencies
    print("\n🔗 Example 4: Multi-step Workflow")
    print("-" * 30)

    # Step 1: Generate research topics
    async def generate_topics():
        """Generate research topics."""
        response = langbase.agent.run(
            input="Generate 3 AI research topics.",
            model="openai:gpt-4o-mini",
            api_key=os.environ.get("LLM_API_KEY"),
        )
        return response["output"]

    # Step 2: Expand on each topic (using context from previous step)
    async def expand_topics():
        """Expand on the generated topics."""
        # Access previous step's output from workflow context
        topics = workflow.context["outputs"].get("research_topics", "")

        response = langbase.agent.run(
            input=f"Expand on these research topics: {topics}",
            model="openai:gpt-4o-mini",
            api_key=os.environ.get("LLM_API_KEY"),
        )
        return response["output"]

    # Step 3: Generate recommendations
    async def generate_recommendations():
        """Generate recommendations based on previous steps."""
        topics = workflow.context["outputs"].get("research_topics", "")
        expansion = workflow.context["outputs"].get("topic_expansion", "")

        response = langbase.agent.run(
            input=f"Based on these topics: {topics}\n\nAnd expansion: {expansion}\n\nGenerate research recommendations.",
            model="openai:gpt-4o-mini",
            api_key=os.environ.get("LLM_API_KEY"),
        )
        return response["completion"]

    try:
        # Execute the multi-step workflow
        topics = await workflow.step(
            {
                "id": "research_topics",
                "timeout": 15000,  # 15 seconds
                "retries": {"limit": 2, "delay": 2000, "backoff": "linear"},
                "run": generate_topics,
            }
        )
        print(f"✅ Topics: {topics[:100]}...")

        expansion = await workflow.step(
            {
                "id": "topic_expansion",
                "timeout": 20000,  # 20 seconds
                "run": expand_topics,
            }
        )
        print(f"✅ Expansion: {expansion[:100]}...")

        recommendations = await workflow.step(
            {
                "id": "final_recommendations",
                "timeout": 15000,
                "run": generate_recommendations,
            }
        )
        print(f"✅ Recommendations: {recommendations[:100]}...")

    except Exception as e:
        print(f"❌ Multi-step workflow failed: {e}")

    # Example 5: Parallel steps (simulated with multiple workflows)
    print("\n⚡ Example 5: Parallel Step Execution")
    print("-" * 30)

    async def generate_technical_content():
        """Generate technical content."""
        response = langbase.agent.run(
            input="Explain quantum computing basics.",
            model="openai:gpt-4o-mini",
            api_key=os.environ.get("LLM_API_KEY"),
        )
        return response["output"]

    async def generate_marketing_content():
        """Generate marketing content."""
        response = langbase.agent.run(
            input="Write marketing copy for a tech product.",
            model="openai:gpt-4o-mini",
            api_key=os.environ.get("LLM_API_KEY"),
        )
        return response["output"]

    # Create separate workflows for parallel execution
    technical_workflow = Workflow(debug=True)
    marketing_workflow = Workflow(debug=True)

    try:
        # Execute steps in parallel
        results = await asyncio.gather(
            technical_workflow.step(
                {
                    "id": "technical_content",
                    "timeout": 15000,
                    "run": generate_technical_content,
                }
            ),
            marketing_workflow.step(
                {
                    "id": "marketing_content",
                    "timeout": 15000,
                    "run": generate_marketing_content,
                }
            ),
            return_exceptions=True,
        )

        technical_result, marketing_result = results

        if isinstance(technical_result, Exception):
            print(f"❌ Technical content failed: {technical_result}")
        else:
            print(f"✅ Technical content: {technical_result[:100]}...")

        if isinstance(marketing_result, Exception):
            print(f"❌ Marketing content failed: {marketing_result}")
        else:
            print(f"✅ Marketing content: {marketing_result[:100]}...")

    except Exception as e:
        print(f"❌ Parallel execution failed: {e}")

    # Display final workflow context
    print("\n📊 Final Workflow Context")
    print("-" * 30)
    print(f"Total steps executed: {len(workflow.context['outputs'])}")
    for step_id, result in workflow.context["outputs"].items():
        result_preview = (
            str(result)[:50] + "..." if len(str(result)) > 50 else str(result)
        )
        print(f"  {step_id}: {result_preview}")

    print("\n🎉 Workflow examples completed!")


# Example of a more complex workflow class
class AIContentWorkflow:
    """
    A specialized workflow class for AI content generation tasks.
    """

    def __init__(self, langbase_client: Langbase, debug: bool = False):
        """
        Initialize the AI content workflow.

        Args:
            langbase_client: Langbase client instance
            debug: Whether to enable debug mode
        """
        self.lb = langbase_client
        self.workflow = Workflow(debug=debug)

    async def generate_blog_post(
        self, topic: str, target_length: str = "medium", tone: str = "professional"
    ) -> dict:
        """
        Generate a complete blog post with multiple steps.

        Args:
            topic: The blog post topic
            target_length: Target length (short, medium, long)
            tone: Writing tone

        Returns:
            Dictionary containing all generated content
        """

        # Step 1: Generate outline
        async def create_outline():
            response = self.lb.agent.run(
                input=f"Create a {target_length} blog post outline about: {topic}",
                model="openai:gpt-4o-mini",
                api_key=os.environ.get("LLM_API_KEY"),
            )
            return response["output"]

        # Step 2: Generate introduction
        async def write_introduction():
            outline = self.workflow.context["outputs"]["outline"]
            response = self.lb.agent.run(
                input=f"Write an engaging introduction for this outline: {outline}. Tone: {tone}",
                model="openai:gpt-4o-mini",
                api_key=os.environ.get("LLM_API_KEY"),
            )
            return response["output"]

        # Step 3: Generate main content
        async def write_main_content():
            outline = self.workflow.context["outputs"]["outline"]
            intro = self.workflow.context["outputs"]["introduction"]
            response = self.lb.agent.run(
                input=f"Write the main content based on outline: {outline}\nIntroduction: {intro}\nTone: {tone}",
                model="openai:gpt-4o-mini",
                api_key=os.environ.get("LLM_API_KEY"),
            )
            return response["output"]

        # Step 4: Generate conclusion
        async def write_conclusion():
            outline = self.workflow.context["outputs"]["outline"]
            content = self.workflow.context["outputs"]["main_content"]
            response = self.lb.agent.run(
                input=f"Write a conclusion for this content: {content[:500]}...",
                model="openai:gpt-4o-mini",
                api_key=os.environ.get("LLM_API_KEY"),
            )
            return response["output"]

        # Execute the workflow
        try:
            outline = await self.workflow.step(
                {
                    "id": "outline",
                    "timeout": 10000,
                    "retries": {"limit": 2, "delay": 1000, "backoff": "fixed"},
                    "run": create_outline,
                }
            )

            introduction = await self.workflow.step(
                {"id": "introduction", "timeout": 15000, "run": write_introduction}
            )

            main_content = await self.workflow.step(
                {
                    "id": "main_content",
                    "timeout": 30000,
                    "retries": {"limit": 1, "delay": 2000, "backoff": "fixed"},
                    "run": write_main_content,
                }
            )

            conclusion = await self.workflow.step(
                {"id": "conclusion", "timeout": 10000, "run": write_conclusion}
            )

            return {
                "topic": topic,
                "outline": outline,
                "introduction": introduction,
                "main_content": main_content,
                "conclusion": conclusion,
                "metadata": {
                    "tone": tone,
                    "target_length": target_length,
                    "steps_executed": len(self.workflow.context["outputs"]),
                },
            }

        except Exception as e:
            print(f"❌ Blog post generation failed: {e}")
            return {
                "error": str(e),
                "partial_results": self.workflow.context["outputs"],
            }


async def advanced_workflow_example():
    """Demonstrate the advanced workflow class."""
    print("\n🚀 Advanced Workflow Example")
    print("=" * 50)

    lb = Langbase(api_key=os.environ.get("LANGBASE_API_KEY"))
    blog_workflow = AIContentWorkflow(lb, debug=True)

    result = await blog_workflow.generate_blog_post(
        topic="The Future of Artificial Intelligence",
        target_length="medium",
        tone="engaging",
    )

    if "error" in result:
        print(f"❌ Workflow failed: {result['error']}")
        if result.get("partial_results"):
            print("Partial results:", result["partial_results"])
    else:
        print("✅ Blog post generated successfully!")
        print(f"📝 Topic: {result['topic']}")
        print(f"📋 Outline: {result['outline'][:100]}...")
        print(f"🎯 Introduction: {result['introduction'][:100]}...")
        print(f"📄 Content: {result['main_content'][:100]}...")
        print(f"🎯 Conclusion: {result['conclusion'][:100]}...")


if __name__ == "__main__":
    # Set up environment variables if not already set
    if not os.getenv("LANGBASE_API_KEY"):
        print("⚠️  Please set LANGBASE_API_KEY environment variable")
        print("   You can get your API key from https://langbase.com/settings")
        exit(1)

    # asyncio.run(main())
    # Run the advanced example
    asyncio.run(advanced_workflow_example())
