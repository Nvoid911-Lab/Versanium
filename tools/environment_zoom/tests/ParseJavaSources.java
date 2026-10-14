// Syntax-only parser. This does not perform Chromium/Android symbol resolution.
import java.nio.file.*;
import java.util.Locale;
import org.eclipse.jdt.internal.compiler.*;
import org.eclipse.jdt.internal.compiler.batch.CompilationUnit;
import org.eclipse.jdt.internal.compiler.classfmt.ClassFileConstants;
import org.eclipse.jdt.internal.compiler.impl.CompilerOptions;
import org.eclipse.jdt.internal.compiler.parser.Parser;
import org.eclipse.jdt.internal.compiler.problem.*;

public final class ParseJavaSources {
    public static void main(String[] paths) throws Exception {
        CompilerOptions options=new CompilerOptions();
        options.sourceLevel=ClassFileConstants.JDK23;
        options.complianceLevel=ClassFileConstants.JDK23;
        Parser parser=new Parser(new ProblemReporter(DefaultErrorHandlingPolicies.proceedWithAllProblems(),
                options,new DefaultProblemFactory(Locale.ROOT)),true);
        int count=0;
        for(String path:paths){
            CompilationUnit unit=new CompilationUnit(Files.readString(Path.of(path)).toCharArray(),path,"UTF-8");
            CompilationResult result=new CompilationResult(unit,0,1,100);
            parser.parse(unit,result);
            if(result.hasErrors())throw new AssertionError(path+"\n"+java.util.Arrays.toString(result.getErrors()));
            count++;
        }
        System.out.println("Java 23 syntax parsed: "+count+" sources (NOT Chromium type checking)");
    }
}
