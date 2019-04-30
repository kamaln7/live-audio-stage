"""
Run this utility to see which midi ports are available
"""

import mido

if __name__ == '__main__':
    backend_name = 'pygame'  # change if you're using another backend
    mido.set_backend('mido.backends.' + backend_name)
    mido.backend
    print mido.get_output_names()
