// Copyright 2026 Versanium contributors. BSD-style test utility.
import java.nio.file.Path;
import java.util.Arrays;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaCompiler;
import javax.tools.JavaFileObject;
import javax.tools.StandardJavaFileManager;
import javax.tools.ToolProvider;
import com.sun.source.util.JavacTask;

/** Parse only: never analyzes dependencies or compiles Chromium classes. */
public final class ParseJavaSources {
    public static void main(String[] args) throws Exception {
        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        DiagnosticCollector<JavaFileObject> diagnostics = new DiagnosticCollector<>();
        try (StandardJavaFileManager files = compiler.getStandardFileManager(diagnostics, null, null)) {
            var inputs = files.getJavaFileObjectsFromPaths(
                    Arrays.stream(args).map(Path::of).toList());
            JavacTask task = (JavacTask) compiler.getTask(
                    null, files, diagnostics, Arrays.asList("-proc:none"), null, inputs);
            task.parse();
            for (var diagnostic : diagnostics.getDiagnostics()) {
                if (diagnostic.getKind() == Diagnostic.Kind.ERROR) {
                    throw new AssertionError(diagnostic.toString());
                }
            }
        }
        System.out.println("PASS: parse-only syntax of " + args.length + " Java sources");
    }
}
