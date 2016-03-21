import sublime
import sublime_plugin


class MoveByParagraphCommand(sublime_plugin.TextCommand):
    
    def findNextVisibleRegion(self, pos):
        region = self.view.find('\n\s*\n+', pos)
        if region:
            
            # Only way to tell if it's folded is to fold it, so stupid.
            temp = sublime.Region(region.end()-1, region.end())
            foldResult = self.view.fold(temp)
            if foldResult:
                self.view.unfold(temp)
                return region
            else:
                return self.findNextVisibleRegion(region.end())
        else:
            return None
    
    def run(self, edit, extend=False, forward=True):
        start = self.view.sel()[0].begin()
        selectionEnd = self.view.sel()[0].end()
        newSelection = None
        if forward:
            region = self.findNextVisibleRegion(selectionEnd)
            if region:
                newSelection = region.end()
            else:
                newSelection = self.view.size()
            self.view.sel().clear()
            if extend:
                self.view.sel().add( sublime.Region(start, newSelection) )
            else:
                self.view.sel().add( sublime.Region(newSelection, newSelection) )
                
        else:
            regions = self.view.find_all('\n\s*\n+')
            for i, region in reversed(list(enumerate(regions))):
                if region.begin() < start:
                    temp = sublime.Region(regions[i-1].end(), regions[i-1].end()+1)
                    foldResult = self.view.fold(temp)
                    if foldResult:
                        self.view.unfold(temp)
                    else:
                        continue
                
                    if i > 0:
                        newSelection = regions[i-1].end()
                    else:
                        newSelection = 0

                    self.view.sel().clear()
                    if extend:
                        self.view.sel().add( sublime.Region(newSelection, selectionEnd) )
                    else:
                        self.view.sel().add( sublime.Region(newSelection, newSelection) )

                    break
            else:
                newSelection = regions[-1].end()
                self.view.sel().clear()
                if extend:
                    self.view.sel().add( sublime.Region(newSelection, selectionEnd) )
                else:
                    self.view.sel().add( sublime.Region(newSelection, newSelection) )
        
        # visible_region() is for if the point is within the viewport
        if newSelection:
            if not self.view.visible_region().contains(newSelection):
                self.view.show_at_center(newSelection)

'''
Testing
    a
    b
    c
    
FOLD ME
    b
    b
    
    c
    c
    
    xx
    xx
    
    yy
    yy

D
    D

E
    E


'''