import random

from fakeidentities.noise.noiser import Noiser


class PhoneNoiser(Noiser[str]):
    p_swap: float = 0.2

    def noise(self, original: str) -> str:
        # Find all digit indices
        digit_indices = [i for i, char in enumerate(original) if char.isdigit()]
        phone_chars = list(original)
        for _ in range(2): # Repeat a few times to swap potentially multiple chars
            if random.random() < 0.2:  # 20% probability
                # Pick a random digit index (excluding first and last)
                swap_idx = random.choice(digit_indices[1:-1])
                # Get valid neighbors (previous or next digit indices in digit_indices)
                current_pos = digit_indices.index(swap_idx)
                neighbors = [digit_indices[current_pos - 1], digit_indices[current_pos + 1]]
                swap_with_idx = random.choice(neighbors)
                # Swap the digits
                phone_chars[swap_idx], phone_chars[swap_with_idx] = (
                    phone_chars[swap_with_idx],
                    phone_chars[swap_idx],
                )

        return "".join(phone_chars)
