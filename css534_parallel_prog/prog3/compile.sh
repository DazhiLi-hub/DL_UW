javac -classpath ${HADOOP_HOME}/hadoop-${HADOOP_VERSION}-core.jar InvertedIndexes.java
jar -cvf InvertedIndexes.jar *.class
