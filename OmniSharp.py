import urllib2, urllib, urlparse, json, os, sublime_plugin, sublime

class OmniSharp(sublime_plugin.EventListener):
    word_list = [] 

    def on_pre_save(self, view):
      self.view = view
      if self.is_dotnet_file(view.scope_name(view.sel()[0].begin())):
          js = self.get_response('/syntaxerrors')
          if len(js['Errors']) > 0 :
            view.set_status('message', 'Syntax errors.  View the console for details')
            print js['Errors']
          else :
            view.set_status('message', '')


    def on_modified(self, view):
        self.view = view
        sublime.set_timeout(lambda: self.load_completions(view), 3)

    def load_completions(self, view):
        scope_name = view.scope_name(view.sel()[0].begin())  
        if self.is_dotnet_file(scope_name) : 
            parameters = {}
            location = self.view.sel()[0]
            parameters['wordToComplete'] = self.view.substr(self.view.word(location.a))
            completions = self.get_response('/autocomplete', parameters) 
            
            for completion in completions:
                self.word_list.append(completion['CompletionText'])

    def is_dotnet_file(self, scope):
        return ".cs" in scope       

    def get_autocomplete_list(self, word):
        autocomplete_list = []
        for w in self.word_list:
            try:
                if word.lower() in w.lower():
                    autocomplete_list.append((w, w))
            except UnicodeDecodeError:
                continue

        return autocomplete_list

    # gets called when auto-completion pops up.
    def on_query_completions(self, view, prefix, locations):
        scope_name = sublime.windows()[0].active_view().scope_name(sublime.windows()[0].active_view().sel()[0].begin())
        return self.get_autocomplete_list(prefix)

    def get_response(self, endpoint, additionalParameters=None):
        parameters = {}
        location = self.view.sel()[0]
        cursor = self.view.rowcol(location.begin()) 
        parameters['line'] = cursor[0] + 1
        parameters['column'] = cursor[1] + 1
        parameters['buffer'] = '\r\n'.join(self.task_input()[:])
        parameters['filename'] = self.view.file_name()

        if additionalParameters != None:
          parameters.update(additionalParameters)

        target =  urlparse.urljoin('http://localhost:2000/', endpoint)
        parameters = urllib.urlencode(parameters)
        response = urllib2.urlopen(target, parameters)

        js = response.read()

        if(js != ''):
            return json.loads(js) 

    def task_input(self):
        selections = [region for region in self.view.sel() if not region.empty()]
        if len(selections) == 0:
            self.regions = [sublime.Region(0, self.view.size())]
        else:
            self.regions = selections

        page_text = [self.view.substr(region).encode('utf-8') for region in self.regions]
        return page_text