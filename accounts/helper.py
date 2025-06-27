import json
import re

raw_text =  "Here are the 20 multiple-choice questions for the CSS exam on English vocabulary:\n\n**11(a): ALACRITY**  \nA. Slowness  \nB. Diligence  \nC. Eagerness  \nD. Wavering  \nCorrect Answer: C\n\n**12(a): EMBRYO**  \nA. Seedling  \nB. Matured stage  \nC. Early stage  \nD. Dead state  \nCorrect Answer: C\n\n**13(a): PRAGMATISM**  \nA. Idealism  \nB. Flexibility  \nC. Theoretical orientation  \nD. Action-oriented approach  \nCorrect Answer: D\n\n**14(a): CONSISTENT**  \nA. Conflicting  \nB. Uniform  \nC. Irregular  \nD. Divisive  \nCorrect Answer: B\n\n**15(a): ELOQUENCE**  \nA. Fluency  \nB. Absence of articulation  \nC. Articulateness  \nD. Lack of clarity  \nCorrect Answer: C\n\n**16(a): PROPENSITY**  \nA. Inclination  \nB. Aversion  \nC. Compulsion  \nD. Constraint  \nCorrect Answer: A\n\n**17(a): MISFORTUNE**  \nA. Calamity  \nB. Good luck  \nC. Unforeseen event  \nD. Common event  \nCorrect Answer: A\n\n**18(a): INFLATION**  \nA. Fall in prices  \nB. Rise in prices  \nC. Deflation  \nD. Stagnation  \nCorrect Answer: B\n\n**19(a): PRINCIPLE**  \nA. Rule  \nB. Moral compass  \nC. Scientific fact  \nD. Absolute truth  \nCorrect Answer: B\n\n**20(a): RESTIVENESS**  \nA. Restlessness  \nB. Calmness  \nC. Inactivity  \nD. Complacency  \nCorrect Answer: A⭐\n\n---\n\n**A1(b): DEMOCRACY**  \nA. Autocracy  \nB. Rule of elites  \nC. Rule by people  \nD. Military rule  \nCorrect Answer: C\n\n**A2(b): DYED-IN-THE-LEATHER**  \nA. Non-resistant  \nB. Unyielding  \nC. Varied  \nD. Changeable  \nCorrect Answer: B\n\n**A3(b): GOVERNANCE**  \nA. Management of affairs  \nB. Withdrawal from involvement  \nC. Degradation  \nD. Obstruction  \nCorrect Answer: A⭐\n\n**A4(b): INTEGRITY**  \nA. Dishonesty  \nB. Honesty  \nC. Ignorance  \nD. Indifference  \nCorrect Answer: B\n\n**A5(b): PERSISTENCE**  \nA. Succession  \nB. Tenacity  \nC. Yielding  \nD. Consistency  \nCorrect Answer: C\n\n**A6(b): ABJECT**  \nA. Noble  \nB. Despicable  \nC. Contented  \nD. Humiliating  \nCorrect Answer: D\n\n**A7(b): COALESCE**  \nA. Converge  \nB. Diverge  \nC. Fragment  \nD. Vanish  \nCorrect Answer: A\n\n**A8(b): ALLEGIANCE**  \nA. Disloyalty  \nB. Commitment  \nC. Indifference  \nD. Secession  \nCorrect Answer: B\n\n**A9(b): PREDILECTION**  \nA. Preference  \nB. Aversion  \nC. Necessity  \nD. Contagion  \nCorrect Answer: A\n\n**A10(b): CYPHER**  \nA. Code  \nB. Enigma  \nC. Clear text  \nD. Precise figure  \nCorrect Answer: A"


def parse_mcqs(text):
    questions = []
    pattern = re.compile(
        r"(?P<id>[\dA-Z]+\(?.?\)?)[:：]?\s*(?P<question>[A-Z \-’'()]+)\n"
        r"A\.\s*(?P<A>.+?)\n"
        r"B\.\s*(?P<B>.+?)\n"
        r"C\.\s*(?P<C>.+?)\n"
        r"D\.\s*(?P<D>.+?)\n"
        r"Correct Answer:\s*(?P<answer>[A-D])",
        re.MULTILINE
    )

    matches = pattern.finditer(text)
    for match in matches:
        q = match.groupdict()
        questions.append({
            "id": q["id"],
            "question": q["question"],
            "options": [q["A"], q["B"], q["C"], q["D"]],
            "correctAnswer": q["answer"]
        })

    return questions
