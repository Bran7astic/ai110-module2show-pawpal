# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
    * My UML design contains the four intended classes, being Owner, Pet, Task, and Scheduler.
- What classes did you include, and what responsibilities did you assign to each?
    *  The owner, pet and task classes hold data and have sensible methods, and the schedule only has methods, as it doesn't function as a dataclass
**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
    * Yes, Copilot didn't include priority and duration on the tasks, which are important for organizing the tasks and scheduling
    * Copilot also added some new fields for tasks, include an ID to make deleting and editing tasks less fragile, and 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
    * Available time per day (minute budget)
    * Due date / time ordering
    * Priority score as a tie-breaker
    * Completion status (completed tasks filtered out of daily plan)
    * Optional preference toggle for earlier due vs priority-first ordering
- How did you decide which constraints mattered most?
    * Time + due date felt most realistic for a busy owner
    * Priority still important, but used after urgency so urgent tasks do not get buried
    * Kept rules simple first, then added smarter filtering + warnings

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
    * Uses greedy selection under time budget, not full optimization
    * Also allows same-time tasks and just warns instead of auto-rescheduling
- Why is that tradeoff reasonable for this scenario?
    * Faster to implement and easier to explain/demo
    * Good enough for this project scope
    * Warnings keep it safe without overcomplicating core logic

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
    * Used AI for UML-to-code scaffolding
    * Helped add incremental features (sorting, filtering, recurrence, conflict detection)
    * Used it for refactors in Streamlit display logic so backend methods were reused
    * Used it to generate + extend tests faster
- What kinds of prompts or questions were most helpful?
    * Specific asks with behavior + constraints, e.g. "mark daily/weekly complete -> create next instance"
    * Prompts that asked for tests along with code changes
    * Prompts that required non-crashing warnings instead of hard errors

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
    * Earlier recurrence handling moved due date on same object
    * Needed history preserved, so changed to create a brand-new next task instance
- How did you evaluate or verify what the AI suggested?
    * Ran `python main.py` and checked printed schedule/warnings
    * Added targeted pytest cases for sorting, recurrence, and conflict behavior
    * Reviewed actual task state changes in UI and tests before keeping changes

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
    * Task completion/incompletion updates
    * Task add/remove basics through owner + pet relationships
    * Sorting correctness (earliest-first, descending, tie-breakers)
    * Filtering by pet and completion status
    * Recurrence parsing + next-instance creation for daily/weekly completion
    * Overlap conflict detection and same-time warning generation
- Why were these tests important?
    * These are the core scheduler paths that drive planning output
    * Protects against regressions when adding new logic
    * Makes confidence in demo behavior much higher

**b. Confidence**

- How confident are you that your scheduler works correctly?
    * About 4/5 confident
    * Main flows covered and behaving as expected
- What edge cases would you test next if you had more time?
    * Multiple pets sharing one recurring task over many weeks
    * Timezone/daylight-saving boundary behavior
    * Very large task lists (performance + deterministic ordering)
    * Invalid/odd frequency strings and graceful fallback behavior
    * Auto-rescheduling suggestions after conflicts (not just warnings)

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
    * I'm most satisfied by seeing the app come together, and the iterative process of testing the backend via CLI, and then integrating it with the frontend

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
    * I'd take more time to understand the suggestions Copilot made, and closely evaluate whether the decisions it makes are the best course of action

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
    * My major takeaway is that AI is a great tool for designing systems, but it still needs a solid foundation decided by humans in order to build a coherent app
