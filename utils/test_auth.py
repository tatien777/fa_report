
import streamlit as st
import collections
import functools

class StopExecution(Exception):
    """Special Exception which does not display any output to the Streamlit app."""
    pass

def cache_on_button_press(label, show_spinner=True):
    """Function decorator to memoize function executions.
    Parameters
    ----------
    label : str
        The label for the button to display prior to running the cached funnction.
    show_spinner : bool
        Whether to show the spinner when evaluating the cached function.
    Example
    -------
    This show how you could write a username/password tester:
    >>> try:
    ...     @cache_on_button_press('Authenticate')
    ...     def authenticate(username, password):
    ...         return username == "buddha" and password == "s4msara"
    ...
    ...     username = st.text_input('username')
    ...     password = st.text_input('password')
    ...     if authenticate(username, password):
    ...         st.success('Logged in.')
    ...     else:
    ...         st.error('Incorrect username or password')
    ... except StopExecution:
    ...     pass
    """
    def function_decorator(func):
        @functools.wraps(func)
        def wrapped_func(*args, **kwargs):
            @st.cache(None,show_spinner=show_spinner)
            def get_cache_entry(func, args, kwargs):
                class ButtonCacheEntry:
                    def __init__(self):
                        self.return_value = None
                        self.evaluated = False
                    def evaluate(self):
                        # We call func() before setting self.evaluated so that
                        # exceptions propagate out properly.
                        self.return_value = func(*args, **kwargs)
                        self.evaluated = True
                return ButtonCacheEntry()
            cache_entry = get_cache_entry(func, args, kwargs)
            if not cache_entry.evaluated:
                if st.button(label):
                    cache_entry.evaluate()
                else:
                    raise StopExecution
            return cache_entry.return_value
        return wrapped_func
    return function_decorator

# @st.cache(allow_output_mutation=True)
def confirm_button_example(def_run=None):
    # st.write("""
    # This example shows a hack to create a "confirm button" in Streamlit, e.g.
    # to authenticate a username / password pair.
    # """)
    # with st.echo():
        try:
            # @st.cache(allow_output_mutation=True)
            # @st.cache(hash_funcs={FooType: hash_func_for_foo_type})
            # @st.cache(suppress_st_warning=True)
            
            @cache_on_button_press('Authenticate')
            def authenticate(username, password):
                return username == "ahamove" and password == "aha-fa-bi"

            username = st.text_input('username')
            password = st.text_input('password')

            if authenticate(username, password):
                return True
            else:
                st.error('The username or password you have entered is invalid.')

        except StopExecution:
            # In the future this try/catch won't be necessary because we
            # could imagine adding StopExecution to the Streamlit and
            # having the ScriptRunner handle it silently.
            pass

if __name__ == '__main__':
    confirm_button_example()